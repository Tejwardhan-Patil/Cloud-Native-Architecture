package main

import (
    "encoding/json"
    "log"
    "net/http"
    "os"
    "time"
    "context"
    "strconv"

    "github.com/gorilla/mux"
)

// Response structure for health checks
type HealthResponse struct {
    Status  string `json:"status"`
    Uptime  string `json:"uptime"`
    Version string `json:"version"`
}

// Response structure for process request
type ProcessResponse struct {
    Status  string `json:"status"`
    Message string `json:"message"`
    Data    interface{} `json:"data"`
}

// Middleware for logging request details
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("Started %s %s", r.Method, r.RequestURI)
        next.ServeHTTP(w, r)
        log.Printf("Completed in %v", time.Since(start))
    })
}

// Middleware for setting basic headers
func setHeadersMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        next.ServeHTTP(w, r)
    })
}

// Global variables to track service state
var startTime time.Time
const version = "1.0.0"

// HealthCheckHandler provides health status of the service
func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
    uptime := time.Since(startTime).String()
    response := HealthResponse{
        Status:  "OK",
        Uptime:  uptime,
        Version: version,
    }
    json.NewEncoder(w).Encode(response)
}

// ProcessHandler handles data processing requests
func ProcessHandler(w http.ResponseWriter, r *http.Request) {
    var requestData map[string]interface{}
    err := json.NewDecoder(r.Body).Decode(&requestData)
    if err != nil {
        http.Error(w, "Invalid request payload", http.StatusBadRequest)
        return
    }

    // Simulating processing of the request
    log.Printf("Processing data: %v", requestData)
    response := ProcessResponse{
        Status:  "Success",
        Message: "Data processed successfully",
        Data:    requestData,
    }

    json.NewEncoder(w).Encode(response)
}

// Handler for graceful shutdown
func GracefulShutdown(server *http.Server, timeout time.Duration) {
    // Listen for OS signals
    stop := make(chan os.Signal, 1)
    <-stop
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    log.Println("Shutting down gracefully...")
    if err := server.Shutdown(ctx); err != nil {
        log.Fatalf("Could not gracefully shutdown the server: %v", err)
    }
    log.Println("Server shut down")
}

// Function to initialize and configure the router
func InitializeRouter() *mux.Router {
    router := mux.NewRouter()

    // Add middleware
    router.Use(loggingMiddleware)
    router.Use(setHeadersMiddleware)

    // Define the routes
    router.HandleFunc("/health", HealthCheckHandler).Methods("GET")
    router.HandleFunc("/process", ProcessHandler).Methods("POST")

    return router
}

// Function to set up and start the HTTP server
func StartServer(router *mux.Router) *http.Server {
    port := os.Getenv("SERVICE_A_PORT")
    if port == "" {
        port = "8080"
    }

    // Convert port to an integer for validation
    portNumber, err := strconv.Atoi(port)
    if err != nil || portNumber < 1 || portNumber > 65535 {
        log.Fatalf("Invalid port number: %s", port)
    }

    server := &http.Server{
        Handler:      router,
        Addr:         ":" + port,
        WriteTimeout: 15 * time.Second,
        ReadTimeout:  15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    log.Printf("Service A is starting on port %s", port)
    return server
}

func main() {
    // Record the start time for uptime calculation
    startTime = time.Now()

    // Initialize the router
    router := InitializeRouter()

    // Set up the server
    server := StartServer(router)

    // Start the server in a goroutine
    go func() {
        if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Service A failed to start: %v", err)
        }
    }()

    // Set up graceful shutdown
    GracefulShutdown(server, 10*time.Second)
}