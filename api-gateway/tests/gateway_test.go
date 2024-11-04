package tests

import (
	"api-gateway/src"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestHealthCheckEndpoint tests the health check route
func TestHealthCheckEndpoint(t *testing.T) {
	req, err := http.NewRequest("GET", "/health", nil)
	assert.NoError(t, err, "Error creating the request")

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(src.HealthCheckHandler)

	handler.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code, "Expected status OK")

	expectedBody := `{"status": "healthy"}`
	assert.JSONEq(t, expectedBody, rr.Body.String(), "Expected JSON response")
}

// TestGatewayRoutes tests routing logic of the API Gateway
func TestGatewayRoutes(t *testing.T) {
	router := src.SetupRouter()

	testCases := []struct {
		method       string
		path         string
		expectedCode int
	}{
		{"GET", "/service-a/resource", http.StatusOK},
		{"POST", "/service-b/action", http.StatusCreated},
		{"PUT", "/service-c/resource/123", http.StatusAccepted},
		{"DELETE", "/service-c/resource/123", http.StatusNoContent},
		{"GET", "/non-existent-route", http.StatusNotFound},
	}

	for _, tc := range testCases {
		req, err := http.NewRequest(tc.method, tc.path, nil)
		assert.NoError(t, err, "Error creating request")

		rr := httptest.NewRecorder()
		router.ServeHTTP(rr, req)

		assert.Equal(t, tc.expectedCode, rr.Code, "Unexpected status code for route %s", tc.path)
	}
}

// TestAuthMiddleware tests the authorization middleware behavior
func TestAuthMiddleware(t *testing.T) {
	router := src.SetupRouter()

	req, err := http.NewRequest("GET", "/protected/resource", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusUnauthorized, rr.Code, "Expected unauthorized without token")

	req.Header.Set("Authorization", "Bearer valid-token")
	rr = httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code, "Expected OK with valid token")
}

// TestRateLimitingMiddleware simulates rate limiting behavior in the API gateway
func TestRateLimitingMiddleware(t *testing.T) {
	router := src.SetupRouter()

	req, err := http.NewRequest("GET", "/service-a/resource", nil)
	assert.NoError(t, err, "Error creating request")

	for i := 0; i < 10; i++ {
		rr := httptest.NewRecorder()
		router.ServeHTTP(rr, req)
		if i < 5 {
			assert.Equal(t, http.StatusOK, rr.Code, "Expected OK response within rate limit")
		} else {
			assert.Equal(t, http.StatusTooManyRequests, rr.Code, "Expected Too Many Requests after rate limit exceeded")
		}
	}
}

// TestCORSHeaders tests if the API Gateway returns correct CORS headers
func TestCORSHeaders(t *testing.T) {
	req, err := http.NewRequest("OPTIONS", "/service-a/resource", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	handler := src.SetupRouter()
	handler.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code, "Expected OK status for CORS preflight")

	assert.Equal(t, "*", rr.Header().Get("Access-Control-Allow-Origin"), "Expected wildcard CORS policy")
	assert.Equal(t, "GET, POST, OPTIONS", rr.Header().Get("Access-Control-Allow-Methods"), "Expected allowed methods")
	assert.Equal(t, "Content-Type, Authorization", rr.Header().Get("Access-Control-Allow-Headers"), "Expected allowed headers")
}

// TestErrorHandling simulates error responses from backend services
func TestErrorHandling(t *testing.T) {
	router := src.SetupRouter()

	req, err := http.NewRequest("GET", "/service-a/error", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusInternalServerError, rr.Code, "Expected internal server error")

	expectedBody := `{"error": "Internal Server Error"}`
	assert.JSONEq(t, expectedBody, rr.Body.String(), "Expected error response")
}

// TestPerformance simulates a performance test by sending a large number of requests
func TestPerformance(t *testing.T) {
	router := src.SetupRouter()

	for i := 0; i < 1000; i++ {
		req, err := http.NewRequest("GET", "/service-a/resource", nil)
		assert.NoError(t, err, "Error creating request")

		rr := httptest.NewRecorder()
		router.ServeHTTP(rr, req)

		assert.Equal(t, http.StatusOK, rr.Code, "Expected OK response for performance test")
	}
}

// TestInvalidMethod tests invalid HTTP methods for certain routes
func TestInvalidMethod(t *testing.T) {
	router := src.SetupRouter()

	req, err := http.NewRequest("PATCH", "/service-a/resource", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusMethodNotAllowed, rr.Code, "Expected method not allowed")
}

// TestJSONBodyParsing tests if JSON bodies are correctly parsed
func TestJSONBodyParsing(t *testing.T) {
	jsonBody := `{"key": "value"}`
	req, err := http.NewRequest("POST", "/service-b/json-endpoint", strings.NewReader(jsonBody))
	assert.NoError(t, err, "Error creating request")

	req.Header.Set("Content-Type", "application/json")

	rr := httptest.NewRecorder()
	router := src.SetupRouter()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code, "Expected OK response for valid JSON")
	expectedResponse := `{"message": "Received", "data": {"key": "value"}}`
	assert.JSONEq(t, expectedResponse, rr.Body.String(), "Expected valid JSON response")
}

// TestMissingContentTypeHeader tests if requests with missing Content-Type headers are handled
func TestMissingContentTypeHeader(t *testing.T) {
	req, err := http.NewRequest("POST", "/service-b/json-endpoint", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	router := src.SetupRouter()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusBadRequest, rr.Code, "Expected bad request for missing Content-Type")
}

// TestTimeout simulates a timeout scenario in the backend service
func TestTimeout(t *testing.T) {
	router := src.SetupRouter()

	req, err := http.NewRequest("GET", "/service-c/timeout", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusGatewayTimeout, rr.Code, "Expected gateway timeout error")
}

// TestRedirects tests if the API Gateway handles redirects properly
func TestRedirects(t *testing.T) {
	router := src.SetupRouter()

	req, err := http.NewRequest("GET", "/redirect", nil)
	assert.NoError(t, err, "Error creating request")

	rr := httptest.NewRecorder()
	router.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusMovedPermanently, rr.Code, "Expected moved permanently for redirect")
	assert.Equal(t, "/new-location", rr.Header().Get("Location"), "Expected redirect to new location")
}
