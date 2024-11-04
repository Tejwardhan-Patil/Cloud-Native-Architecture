package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"services/service-a/src"
	"testing"
)

// Helper function to load config for multiple tests
func loadTestConfig() error {
	return src.LoadConfig("config/test_config.yaml")
}

// TestMainHandler verifies the main handler of the service
func TestMainHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatalf("Failed to create a request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.MainHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	expected := `{"message": "Hello from service-a"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}

// TestPostHandler checks the POST method with JSON payload
func TestPostHandler(t *testing.T) {
	payload := map[string]string{
		"key": "value",
	}
	payloadBytes, _ := json.Marshal(payload)
	req, err := http.NewRequest("POST", "/post", bytes.NewBuffer(payloadBytes))
	if err != nil {
		t.Fatalf("Failed to create a POST request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.PostHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusCreated {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusCreated)
	}

	expected := `{"status": "success"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}

// TestInvalidMethod checks the service's behavior on invalid HTTP methods
func TestInvalidMethod(t *testing.T) {
	req, err := http.NewRequest("PUT", "/", nil)
	if err != nil {
		t.Fatalf("Failed to create a PUT request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.MainHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusMethodNotAllowed {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusMethodNotAllowed)
	}
}

// TestNotFoundRoute checks how the service responds to undefined routes
func TestNotFoundRoute(t *testing.T) {
	req, err := http.NewRequest("GET", "/undefined-route", nil)
	if err != nil {
		t.Fatalf("Failed to create request for undefined route: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.MainHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusNotFound {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusNotFound)
	}
}

// TestInternalError simulates a server error
func TestInternalError(t *testing.T) {
	req, err := http.NewRequest("GET", "/cause-error", nil)
	if err != nil {
		t.Fatalf("Failed to create a request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.ErrorHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusInternalServerError {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusInternalServerError)
	}

	expected := `{"error": "internal server error"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}

// TestConfigLoad verifies that configuration is loaded properly
func TestConfigLoad(t *testing.T) {
	err := loadTestConfig()
	if err != nil {
		t.Fatalf("Failed to load test config: %v", err)
	}

	if src.Config.ServiceName != "service-a" {
		t.Errorf("Expected service name 'service-a', got %v", src.Config.ServiceName)
	}
}

// TestInvalidConfig verifies handling of invalid config files
func TestInvalidConfig(t *testing.T) {
	os.Rename("config/test_config.yaml", "config/test_config_backup.yaml")
	defer os.Rename("config/test_config_backup.yaml", "config/test_config.yaml")

	err := src.LoadConfig("config/invalid_config.yaml")
	if err == nil {
		t.Fatal("Expected an error when loading invalid config, but got none")
	}
}

// TestTimeout checks for request timeout handling
func TestTimeout(t *testing.T) {
	req, err := http.NewRequest("GET", "/timeout", nil)
	if err != nil {
		t.Fatalf("Failed to create a request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.TimeoutHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusRequestTimeout {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusRequestTimeout)
	}

	expected := `{"error": "request timeout"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}

// TestUnauthorized checks for unauthorized access
func TestUnauthorized(t *testing.T) {
	req, err := http.NewRequest("GET", "/protected", nil)
	if err != nil {
		t.Fatalf("Failed to create a request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.ProtectedHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusUnauthorized {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusUnauthorized)
	}

	expected := `{"error": "unauthorized"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}

// TestRateLimit simulates rate-limiting behavior
func TestRateLimit(t *testing.T) {
	req, err := http.NewRequest("GET", "/rate-limit", nil)
	if err != nil {
		t.Fatalf("Failed to create a request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.RateLimitHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusTooManyRequests {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusTooManyRequests)
	}

	expected := `{"error": "too many requests"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}

// TestConfigReload verifies that the service supports config reloading
func TestConfigReload(t *testing.T) {
	err := loadTestConfig()
	if err != nil {
		t.Fatalf("Failed to load test config: %v", err)
	}

	err = src.ReloadConfig()
	if err != nil {
		t.Fatalf("Failed to reload config: %v", err)
	}

	if src.Config.ServiceName != "service-a" {
		t.Errorf("Expected service name 'service-a' after reload, got %v", src.Config.ServiceName)
	}
}

// TestGracefulShutdown verifies that the service shuts down gracefully
func TestGracefulShutdown(t *testing.T) {
	req, err := http.NewRequest("POST", "/shutdown", nil)
	if err != nil {
		t.Fatalf("Failed to create shutdown request: %v", err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.ShutdownHandler)

	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("Handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	expected := `{"message": "shutdown in progress"}`
	if rr.Body.String() != expected {
		t.Errorf("Handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}
