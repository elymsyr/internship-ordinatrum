using Microsoft.AspNetCore.Mvc;
using PrometheusMetricsAPI.Models;
using System.Collections.Generic;

namespace PrometheusMetricsAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MonitoringController : ControllerBase
    {
        // POST api/monitoring/metrics
        [HttpPost("metrics")]
        public IActionResult PostMetrics([FromBody] List<MetricData> metrics)
        {
            Console.WriteLine("POST GOT");
            if (metrics == null || metrics.Count == 0)
            {
                return BadRequest("No metrics provided.");
            }

            // Process the received data (e.g., log it, save it to a database, etc.)
            foreach (var metric in metrics)
            {
                // Just log the received data for this example
                Console.WriteLine($"Metric: {metric.MetricName}, Value: {metric.Value}");
            }

            // Return a success response
            return Ok(new { message = "Metrics received successfully", metricsCount = metrics.Count });
        }
    }
}
