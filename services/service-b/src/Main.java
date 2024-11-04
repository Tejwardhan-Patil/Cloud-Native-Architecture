import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

@SpringBootApplication
public class Main {

    private static final Logger logger = LoggerFactory.getLogger(Main.class);
    private static final int THREAD_POOL_SIZE = 10;

    private ExecutorService executorService;

    public static void main(String[] args) {
        SpringApplication.run(Main.class, args);
    }

    @Bean
    public CommandLineRunner init() {
        return args -> {
            logger.info("Initializing Service B...");
            initializeResources();
            startBackgroundTasks();
        };
    }

    /**
     * Initialize necessary resources for the service.
     */
    private void initializeResources() {
        logger.info("Setting up resources...");
        executorService = Executors.newFixedThreadPool(THREAD_POOL_SIZE);
        logger.info("Resources initialized successfully.");
    }

    /**
     * Start any necessary background tasks or processes for this service.
     */
    private void startBackgroundTasks() {
        logger.info("Starting background tasks...");
        for (int i = 0; i < THREAD_POOL_SIZE; i++) {
            executorService.submit(() -> {
                try {
                    logger.info("Background task started by thread: {}", Thread.currentThread().getName());
                    performTask();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    logger.error("Task interrupted: {}", e.getMessage());
                }
            });
        }
        logger.info("Background tasks started successfully.");
    }

    /**
     * Perform a sample task as part of the background process.
     */
    private void performTask() throws InterruptedException {
        logger.info("Performing task...");
        // Simulate task processing time
        TimeUnit.SECONDS.sleep(2);
        logger.info("Task completed by thread: {}", Thread.currentThread().getName());
    }

    /**
     * Gracefully shutdown the service and release all resources.
     */
    public void shutdownService() {
        logger.info("Shutting down Service B...");
        if (executorService != null) {
            executorService.shutdown();
            try {
                if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                    logger.warn("Forcing shutdown of background tasks.");
                    executorService.shutdownNow();
                }
            } catch (InterruptedException e) {
                logger.error("Shutdown interrupted: {}", e.getMessage());
                Thread.currentThread().interrupt();
            }
        }
        logger.info("Service B shut down completed.");
    }

    /**
     * Simulate service health check endpoint.
     * This method can be exposed as a REST API to monitor service health.
     *
     * @return boolean representing the health status of the service.
     */
    public boolean healthCheck() {
        logger.info("Performing health check...");
        // Simulate some logic to determine if the service is healthy
        boolean isHealthy = true;
        logger.info("Health check result: {}", isHealthy ? "HEALTHY" : "UNHEALTHY");
        return isHealthy;
    }

    /**
     * Handles critical errors and performs necessary cleanup.
     */
    public void handleError(Exception e) {
        logger.error("Critical error occurred: {}", e.getMessage());
        shutdownService();
        logger.info("Service B has handled the error and cleaned up resources.");
    }

    /**
     * Simulate reading configuration from external sources such as a file or environment variables.
     */
    public void loadConfiguration() {
        logger.info("Loading configuration...");
        // Simulate loading configuration
        try {
            TimeUnit.SECONDS.sleep(1);
            logger.info("Configuration loaded successfully.");
        } catch (InterruptedException e) {
            logger.error("Error loading configuration: {}", e.getMessage());
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Simulate a task that requires retry logic in case of failure.
     */
    public void executeTaskWithRetry() {
        int maxRetries = 3;
        int attempts = 0;
        boolean success = false;
        while (attempts < maxRetries && !success) {
            try {
                logger.info("Attempting to execute task, attempt: {}", attempts + 1);
                performTask();
                success = true;
                logger.info("Task executed successfully.");
            } catch (InterruptedException e) {
                attempts++;
                logger.error("Task failed, attempt: {}", attempts);
                if (attempts >= maxRetries) {
                    logger.error("Max retry attempts reached. Task failed.");
                }
            }
        }
    }

    /**
     * Simulate a periodic task that runs every fixed interval.
     */
    public void schedulePeriodicTask() {
        logger.info("Scheduling periodic task...");
        executorService.scheduleAtFixedRate(() -> {
            try {
                logger.info("Executing periodic task...");
                performTask();
            } catch (InterruptedException e) {
                logger.error("Periodic task interrupted: {}", e.getMessage());
                Thread.currentThread().interrupt();
            }
        }, 0, 5, TimeUnit.SECONDS);
        logger.info("Periodic task scheduled.");
    }

    /**
     * Main business logic for Service B.
     * Implements the core service logic such as data fetching, processing, and saving.
     */
    public void runBusinessLogic() {
        logger.info("Running core business logic...");
        
        try {
            // Fetch Data
            List<String> records = fetchData();
            
            if (records.isEmpty()) {
                logger.warn("No records found to process.");
                return;
            }

            // Process Data
            List<String> processedRecords = processRecords(records);

            // Save or Forward Processed Data
            saveProcessedData(processedRecords);

            logger.info("Business logic executed successfully.");
        } catch (InterruptedException e) {
            logger.error("Error during business logic execution: {}", e.getMessage());
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            logger.error("Unexpected error during business logic execution: {}", e.getMessage());
        }
    }

    /**
     * Fetch data that needs to be processed.
     * @return a list of records to process.
     */
    private List<String> fetchData() {
        logger.info("Fetching records from data source...");
        // Simulate fetching data from a data source
        return Arrays.asList("Data1", "Data2", "Data3");
    }

    /**
     * Process the fetched records.
     * @param records the list of records to process.
     * @return a list of processed records.
     */
    private List<String> processRecords(List<String> records) throws InterruptedException {
        logger.info("Processing records...");
        List<String> processedRecords = new ArrayList<>();
        
        for (String record : records) {
            // Simulate some processing logic for each record
            logger.info("Processing record: {}", record);
            TimeUnit.SECONDS.sleep(1);  // Simulating processing delay
            processedRecords.add(record + "_processed");
        }

        logger.info("Records processed successfully.");
        return processedRecords;
    }

    /**
     * Save or forward the processed records to another service or data store.
     * @param processedRecords the list of processed records.
     */
    private void saveProcessedData(List<String> processedRecords) {
        logger.info("Saving processed records...");
        for (String record : processedRecords) {
            // Simulate saving each record (e.g., to a database or forwarding to another service)
            logger.info("Saved record: {}", record);
        }
        logger.info("All processed records saved successfully.");
    }

    /**
     * Simulate sending notifications in case of critical failures or important events.
     */
    public void sendNotification(String message) {
        logger.info("Sending notification: {}", message);
        // Simulate sending notification logic (email, SMS)
        try {
            TimeUnit.SECONDS.sleep(1);
            logger.info("Notification sent successfully.");
        } catch (InterruptedException e) {
            logger.error("Error sending notification: {}", e.getMessage());
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Simulate some data processing task.
     */
    public void processData() {
        logger.info("Starting data processing...");
        try {
            TimeUnit.SECONDS.sleep(3);
            logger.info("Data processed successfully.");
        } catch (InterruptedException e) {
            logger.error("Error during data processing: {}", e.getMessage());
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Simulate a graceful shutdown handler when the service is stopped.
     */
    @PreDestroy
    public void onShutdown() {
        logger.info("Service B is shutting down...");
        shutdownService();
        logger.info("Service B shutdown completed.");
    }
}