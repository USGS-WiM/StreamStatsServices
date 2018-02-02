using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using StreamStatsAgent;
using Microsoft.AspNetCore.Mvc;
using WiM.Services.Middleware;
using WiM.Services.Analytics;
using WiM.Utilities.ServiceAgent;
using WiM.Services.Resources;
using StreamStatsServices.Filters;

namespace StreamStatsServices
{
    public class Startup
    {
        public Startup(IHostingEnvironment env)
        {
            var builder = new ConfigurationBuilder()
                .SetBasePath(env.ContentRootPath)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
            .AddJsonFile($"appsettings.{env.EnvironmentName}.json", optional: true)
            .AddEnvironmentVariables();
            if (env.IsDevelopment()) {
                //builder.AddApplicationInsightsSettings(developerMode: true);
            }

            Configuration = builder.Build();
        }//end startup       

        public IConfigurationRoot Configuration { get; }

        //Method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            //add functionality to inject IOptions<T>
            services.AddOptions();
            //Configure injectable objs
            services.Configure<APIConfigSettings>(Configuration.GetSection("APIConfigSettings"));
            services.Configure<StreamStatsAgent.Resources.Settings>(Configuration.GetSection("AppSettings"));

            //Add framework services
            services.AddScoped<IStreamStatsAgent, StreamStatsAgent.StreamStatsAgent>();
            services.AddScoped<IAnalyticsAgent, GoogleAnalyticsAgent>((gaa)=> new GoogleAnalyticsAgent(Configuration["AnalyticsKey"]));
            services.AddCors(options =>
            {
                options.AddPolicy("CorsPolicy", builder => builder.AllowAnyOrigin()
                                                                 .AllowAnyMethod()
                                                                 .AllowAnyHeader()
                                                                 .AllowCredentials());
            });

            services.AddMvc(options => { options.RespectBrowserAcceptHeader = true;
                options.Filters.Add(new StreamStatsHypermedia());})                               
                                .AddJsonOptions(options => loadJsonOptions(options));                                
                                
        }     

        // Method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IHostingEnvironment env, ILoggerFactory loggerFactory)
        {
            loggerFactory.AddConsole(Configuration.GetSection("Logging"));
            loggerFactory.AddDebug();

            app.UseCors("CorsPolicy");
            app.Use_Analytics();
            app.UseX_Messages();

            app.UseMvc();            
        }

        #region Helper Methods
        private void loadJsonOptions(MvcJsonOptions options)
        {
            options.SerializerSettings.ReferenceLoopHandling = Newtonsoft.Json.ReferenceLoopHandling.Ignore;
            options.SerializerSettings.MissingMemberHandling = Newtonsoft.Json.MissingMemberHandling.Ignore;
            options.SerializerSettings.NullValueHandling = Newtonsoft.Json.NullValueHandling.Ignore;
            options.SerializerSettings.TypeNameHandling = Newtonsoft.Json.TypeNameHandling.None;
            options.SerializerSettings.TypeNameAssemblyFormatHandling = Newtonsoft.Json.TypeNameAssemblyFormatHandling.Simple;
            options.SerializerSettings.Formatting = Newtonsoft.Json.Formatting.None;
        }
        #endregion
    }
}
