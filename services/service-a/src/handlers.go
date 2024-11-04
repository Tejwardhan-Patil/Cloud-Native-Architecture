package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

// Response defines the standard response structure
type Response struct {
	Status  int         `json:"status"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
	Time    string      `json:"time,omitempty"`
}

// ErrorResponse defines a structure for error responses
type ErrorResponse struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
	Error   string `json:"error"`
}

// RequestLog is a structure for logging incoming requests
type RequestLog struct {
	Method     string `json:"method"`
	URI        string `json:"uri"`
	RemoteAddr string `json:"remote_addr"`
	Time       string `json:"time"`
}

// LogRequest logs details about the incoming request
func LogRequest(r *http.Request) {
	logEntry := RequestLog{
		Method:     r.Method,
		URI:        r.RequestURI,
		RemoteAddr: r.RemoteAddr,
		Time:       time.Now().Format(time.RFC3339),
	}
	logRequestDetails(logEntry)
}

// logRequestDetails prints request details to the log
func logRequestDetails(logEntry RequestLog) {
	logString, err := json.Marshal(logEntry)
	if err != nil {
		log.Printf("Error marshalling request log: %v", err)
	} else {
		log.Printf("Request Received: %s", logString)
	}
}

// HandleHealthCheck handles the health check requests
func HandleHealthCheck(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	response := Response{
		Status:  http.StatusOK,
		Message: "Service A is healthy",
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// HandleGetData handles requests for data retrieval
func HandleGetData(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	// Data retrieval
	data := map[string]string{
		"item1": "value1",
		"item2": "value2",
		"item3": "value3",
	}

	response := Response{
		Status:  http.StatusOK,
		Message: "Data retrieved successfully",
		Data:    data,
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// HandlePostData handles requests to submit data
func HandlePostData(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Printf("Error reading request body: %v", err)
		errorResponse(w, http.StatusBadRequest, "Unable to read request body", err.Error())
		return
	}

	var input map[string]interface{}
	err = json.Unmarshal(body, &input)
	if err != nil {
		log.Printf("Error decoding JSON: %v", err)
		errorResponse(w, http.StatusBadRequest, "Invalid JSON format", err.Error())
		return
	}

	log.Printf("Received data: %v", input)

	response := Response{
		Status:  http.StatusOK,
		Message: "Data processed successfully",
		Data:    input,
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// HandleUpdateData handles data updates
func HandleUpdateData(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Printf("Error reading request body: %v", err)
		errorResponse(w, http.StatusBadRequest, "Unable to read request body", err.Error())
		return
	}

	var updateData map[string]interface{}
	err = json.Unmarshal(body, &updateData)
	if err != nil {
		log.Printf("Error decoding JSON: %v", err)
		errorResponse(w, http.StatusBadRequest, "Invalid JSON format", err.Error())
		return
	}

	log.Printf("Data to update: %v", updateData)

	response := Response{
		Status:  http.StatusOK,
		Message: "Data updated successfully",
		Data:    updateData,
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// HandleDeleteData handles data deletion
func HandleDeleteData(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	query := r.URL.Query()
	id := query.Get("id")

	if id == "" {
		errorResponse(w, http.StatusBadRequest, "Missing id parameter", "id is required to delete an item")
		return
	}

	log.Printf("Deleting item with ID: %s", id)

	response := Response{
		Status:  http.StatusOK,
		Message: "Data deleted successfully",
		Data:    map[string]string{"deleted_id": id},
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// jsonResponse sends a JSON response to the client
func jsonResponse(w http.ResponseWriter, data Response, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	err := json.NewEncoder(w).Encode(data)
	if err != nil {
		log.Printf("Error encoding JSON response: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
}

// errorResponse sends an error response
func errorResponse(w http.ResponseWriter, statusCode int, message string, errDetails string) {
	response := ErrorResponse{
		Status:  statusCode,
		Message: message,
		Error:   errDetails,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	err := json.NewEncoder(w).Encode(response)
	if err != nil {
		log.Printf("Error encoding error response: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
}

// HandleFileUpload handles file uploads
func HandleFileUpload(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	file, header, err := r.FormFile("uploadfile")
	if err != nil {
		log.Printf("Error retrieving the file: %v", err)
		errorResponse(w, http.StatusBadRequest, "Failed to upload file", err.Error())
		return
	}
	defer file.Close()

	log.Printf("Received file: %s", header.Filename)

	response := Response{
		Status:  http.StatusOK,
		Message: "File uploaded successfully",
		Data:    map[string]string{"filename": header.Filename},
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// HandleFileDownload handles file download requests
func HandleFileDownload(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	filename := r.URL.Query().Get("filename")
	if filename == "" {
		errorResponse(w, http.StatusBadRequest, "Missing filename parameter", "Filename is required for download")
		return
	}

	log.Printf("File to download: %s", filename)

	// Stub for file download logic
	w.Header().Set("Content-Disposition", "attachment; filename="+filename)
	w.Header().Set("Content-Type", "application/octet-stream")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("file content"))
}

// HandleLoggingRequest demonstrates logging different request aspects
func HandleLoggingRequest(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	log.Printf("Headers: %v", r.Header)
	log.Printf("Query Params: %v", r.URL.Query())

	response := Response{
		Status:  http.StatusOK,
		Message: "Logging details complete",
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}

// HandleComplexJSON handles complex JSON request and response
func HandleComplexJSON(w http.ResponseWriter, r *http.Request) {
	LogRequest(r)

	var complexInput struct {
		User    string                 `json:"user"`
		Details map[string]interface{} `json:"details"`
	}

	err := json.NewDecoder(r.Body).Decode(&complexInput)
	if err != nil {
		log.Printf("Error decoding complex JSON: %v", err)
		errorResponse(w, http.StatusBadRequest, "Invalid complex JSON format", err.Error())
		return
	}

	log.Printf("Received complex input: %v", complexInput)

	response := Response{
		Status:  http.StatusOK,
		Message: "Complex JSON processed",
		Data:    complexInput,
		Time:    time.Now().Format(time.RFC3339),
	}
	jsonResponse(w, response, http.StatusOK)
}
