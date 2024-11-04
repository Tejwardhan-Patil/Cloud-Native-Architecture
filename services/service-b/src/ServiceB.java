import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * ServiceB.java
 * This class handles the core logic for ServiceB microservice.
 * It contains multiple endpoints for health checks, service info, and utility methods.
 */
@RestController
@RequestMapping("/serviceb")
public class ServiceB {

    private static final Logger logger = LoggerFactory.getLogger(ServiceB.class);

    @Value("${serviceb.message:ServiceB is running}")
    private String message;

    /**
     * Health check endpoint to verify if ServiceB is healthy.
     * @return A message indicating the service is healthy, along with the current timestamp.
     */
    @GetMapping("/health")
    public String healthCheck() {
        logger.info("Health check endpoint called");
        return "ServiceB is healthy: " + LocalDateTime.now();
    }

    /**
     * Get service information endpoint.
     * @return A message that includes the service information and current timestamp.
     */
    @GetMapping("/info")
    public String getServiceInfo() {
        logger.info("Service info endpoint called");
        return "ServiceB Info: " + message + " | Time: " + LocalDateTime.now();
    }

    /**
     * Returns a list of services connected to ServiceB.
     * @return A list of service names.
     */
    @GetMapping("/connected-services")
    public List<String> getConnectedServices() {
        logger.info("Connected services endpoint called");
        List<String> services = new ArrayList<>();
        services.add("ServiceA");
        services.add("ServiceC");
        services.add("ServiceD");
        return services;
    }

    /**
     * Simulates a heavy computation task.
     * This method is for testing resource utilization.
     * @return A message indicating the task is complete.
     */
    @GetMapping("/heavy-task")
    public String performHeavyTask() {
        logger.info("Heavy task endpoint called");
        simulateHeavyComputation();
        return "Heavy task completed at " + LocalDateTime.now();
    }

    /**
     * Simulates heavy computation by performing a calculation.
     */
    private void simulateHeavyComputation() {
        logger.debug("Simulating heavy computation");
        long sum = 0;
        for (long i = 0; i < 1000000000L; i++) {
            sum += i;
        }
        logger.debug("Computation complete with result: " + sum);
    }

    /**
     * Get the current server time.
     * @return The current timestamp.
     */
    @GetMapping("/current-time")
    public String getCurrentTime() {
        logger.info("Current time endpoint called");
        return "Current server time: " + LocalDateTime.now();
    }

    /**
     * Simulates database fetch operation.
     * @return A list of mock data fetched from the database.
     */
    @GetMapping("/fetch-data")
    public List<String> fetchDataFromDatabase() {
        logger.info("Fetching data from database endpoint called");
        return simulateDatabaseFetch();
    }

    /**
     * Simulates fetching data from a database.
     * @return A list of sample data.
     */
    private List<String> simulateDatabaseFetch() {
        logger.debug("Simulating database fetch operation");
        List<String> data = new ArrayList<>();
        data.add("Data 1");
        data.add("Data 2");
        data.add("Data 3");
        return data;
    }

    /**
     * Get system uptime.
     * @return The system uptime in hours.
     */
    @GetMapping("/uptime")
    public String getSystemUptime() {
        logger.info("Uptime endpoint called");
        long uptime = getUptime();
        return "System uptime: " + uptime + " hours";
    }

    /**
     * Simulates retrieving system uptime.
     * @return Uptime in hours.
     */
    private long getUptime() {
        logger.debug("Calculating system uptime");
        long uptime = 500; // Simulated uptime in hours
        return uptime;
    }

    /**
     * Simulates memory usage statistics.
     * @return Memory usage information.
     */
    @GetMapping("/memory-usage")
    public String getMemoryUsage() {
        logger.info("Memory usage endpoint called");
        long memoryUsage = simulateMemoryUsage();
        return "Memory usage: " + memoryUsage + "MB";
    }

    /**
     * Simulates calculation of memory usage.
     * @return Memory usage in MB.
     */
    private long simulateMemoryUsage() {
        logger.debug("Simulating memory usage");
        return 1024; // Simulated memory usage in MB
    }

    /**
     * Endpoint to trigger cache clear operation.
     * @return A message indicating cache clear status.
     */
    @GetMapping("/clear-cache")
    public String clearCache() {
        logger.info("Cache clear endpoint called");
        clearServiceCache();
        return "Cache cleared successfully at " + LocalDateTime.now();
    }

    /**
     * Simulates cache clearing operation.
     */
    private void clearServiceCache() {
        logger.debug("Clearing cache");
    }

    /**
     * Retrieves the status of ServiceB.
     * @return Status message.
     */
    @GetMapping("/status")
    public String getStatus() {
        logger.info("Status endpoint called");
        return "ServiceB status: Running smoothly at " + LocalDateTime.now();
    }

    /**
     * Endpoint for getting detailed application statistics.
     * @return Application statistics in JSON format.
     */
    @GetMapping("/stats")
    public String getApplicationStats() {
        logger.info("Application stats endpoint called");
        return generateApplicationStats();
    }

    /**
     * Simulates generation of application statistics.
     * @return Statistics in a string format.
     */
    private String generateApplicationStats() {
        logger.debug("Generating application statistics");
        String stats = "{\n" +
                "  \"uptime\": \"500 hours\",\n" +
                "  \"memoryUsage\": \"1024 MB\",\n" +
                "  \"connectedServices\": 3,\n" +
                "  \"tasksCompleted\": 1500\n" +
                "}";
        return stats;
    }

    /**
     * Endpoint for system shutdown simulation.
     * @return A message indicating shutdown status.
     */
    @GetMapping("/shutdown")
    public String shutdownSystem() {
        logger.info("Shutdown endpoint called");
        return simulateShutdown();
    }

    /**
     * Simulates system shutdown operation.
     * @return Shutdown status message.
     */
    private String simulateShutdown() {
        logger.warn("Simulating system shutdown");
        return "System shutting down at " + LocalDateTime.now();
    }
}