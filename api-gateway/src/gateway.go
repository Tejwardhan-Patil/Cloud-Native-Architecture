package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"gopkg.in/yaml.v2"
)

// Route represents a single route in the API Gateway configuration
type Route struct {
	Path    string `yaml:"path"`
	Method  string `yaml:"method"`
	Backend string `yaml:"backend"`
}

// GatewayConfig holds all routes for the API Gateway
type GatewayConfig struct {
	Routes []Route `yaml:"routes"`
}

// global variable to store gateway configuration
var gatewayConfig GatewayConfig

// Logger function to provide detailed logging of requests and responses
func logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("Started %s %s", r.Method, r.URL.Path)

		// Call the next handler in the chain
		next.ServeHTTP(w, r)

		// Log the completion of the request
		log.Printf("Completed in %v", time.Since(start))
	})
}

// Load gateway configuration from a YAML file
func loadConfig() {
	configFile := "./config/gateway_config.yaml"

	yamlFile, err := ioutil.ReadFile(configFile)
	if err != nil {
		log.Fatalf("Error reading config file: %s", err)
	}

	err = yaml.Unmarshal(yamlFile, &gatewayConfig)
	if err != nil {
		log.Fatalf("Error parsing config file: %s", err)
	}
}

// Handles proxying the request to the backend service
func proxyRequest(backendURL string, res http.ResponseWriter, req *http.Request) {
	client := &http.Client{
		Timeout: 15 * time.Second,
	}

	// Copying the incoming request into the backend request
	proxyReq, err := http.NewRequest(req.Method, backendURL, req.Body)
	if err != nil {
		http.Error(res, "Failed to create backend request", http.StatusInternalServerError)
		log.Printf("Request error: %s", err)
		return
	}

	proxyReq.Header = req.Header.Clone()

	// Forward the request to the backend service
	resp, err := client.Do(proxyReq)
	if err != nil {
		http.Error(res, "Failed to forward request", http.StatusBadGateway)
		log.Printf("Backend request failed: %s", err)
		return
	}
	defer resp.Body.Close()

	copyResponse(resp, res)
}

// Copy the response from backend to the original response writer
func copyResponse(resp *http.Response, res http.ResponseWriter) {
	res.WriteHeader(resp.StatusCode)
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(res, "Error reading backend response", http.StatusInternalServerError)
		log.Printf("Error reading response: %s", err)
		return
	}
	_, err = res.Write(body)
	if err != nil {
		log.Printf("Error writing response: %s", err)
	}
}

// Function to handle unmatched routes
func handleNotFound(res http.ResponseWriter, req *http.Request) {
	res.WriteHeader(http.StatusNotFound)
	res.Header().Set("Content-Type", "application/json")
	errResponse := map[string]string{"error": "Route not found"}
	jsonResp, _ := json.Marshal(errResponse)
	res.Write(jsonResp)
	log.Printf("404 Route not found: %s", req.URL.Path)
}

// Function to map incoming requests to backend services
func handleRequest(res http.ResponseWriter, req *http.Request) {
	for _, route := range gatewayConfig.Routes {
		if req.URL.Path == route.Path && req.Method == route.Method {
			log.Printf("Forwarding request to backend: %s", route.Backend)
			proxyRequest(route.Backend, res, req)
			return
		}
	}
	handleNotFound(res, req)
}

// Simple health check handler for monitoring the gateway status
func healthCheckHandler(res http.ResponseWriter, req *http.Request) {
	res.WriteHeader(http.StatusOK)
	res.Header().Set("Content-Type", "application/json")
	healthResponse := map[string]string{
		"status":  "ok",
		"message": "API Gateway is healthy",
	}
	jsonResp, _ := json.Marshal(healthResponse)
	res.Write(jsonResp)
}

// CORS Middleware to handle preflight requests
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

// Middleware to ensure API Gateway handles JSON content correctly
func jsonMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !strings.Contains(r.Header.Get("Content-Type"), "application/json") && r.Method != "GET" {
			http.Error(w, "Invalid content type", http.StatusUnsupportedMediaType)
			return
		}
		next.ServeHTTP(w, r)
	})
}

// Main function to set up the API Gateway
func main() {
	loadConfig() // Load the routes from config file

	r := mux.NewRouter()

	// Apply middlewares
	r.Use(logger)
	r.Use(corsMiddleware)
	r.Use(jsonMiddleware)

	// Setting up routes from config
	for _, route := range gatewayConfig.Routes {
		r.HandleFunc(route.Path, handleRequest).Methods(route.Method)
	}

	// Health check route
	r.HandleFunc("/health", healthCheckHandler).Methods("GET")

	// Setting up server configurations
	port := os.Getenv("GATEWAY_PORT")
	if port == "" {
		port = "8080"
	}

	srv := &http.Server{
		Handler:      r,
		Addr:         fmt.Sprintf(":%s", port),
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Printf("API Gateway running on port %s", port)
	err := srv.ListenAndServe()
	if err != nil {
		log.Fatalf("Server failed to start: %s", err)
	}
}
