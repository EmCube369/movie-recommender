package com.marshal.movierecommender.exception;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
	
	@ExceptionHandler(MovieNotFoundException.class)
	public ResponseEntity<Map<String, Object>> handleValidationException(MovieNotFoundException ex) {
		
		Map<String, Object> error = new HashMap<>();
		
		error.put("status", HttpStatus.NOT_FOUND.value());
		error.put("message", ex.getMessage());
		
		return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
	}
	
	@ExceptionHandler(MethodArgumentNotValidException.class)
	public ResponseEntity<Map<String, Object>> handlerResponseStatusException(MethodArgumentNotValidException ex) {
		
		Map<String, Object> errors = new HashMap<>();
		
		ex.getBindingResult().getFieldErrors().forEach(error -> errors.put(error.getField(), error.getDefaultMessage()));
		
		
		return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errors);
	}

}
