package com.marshal.movierecommender.exception;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import com.marshal.movierecommender.recommendation.exception.InvalidRecommendationRequestException;
import com.marshal.movierecommender.recommendation.exception.MlServiceException;
import com.marshal.movierecommender.recommendation.exception.MlServiceUnavailableException;
import com.marshal.movierecommender.recommendation.exception.MlUserNotFoundException;
import com.marshal.movierecommender.recommendation.exception.MlMovieNotFoundException;

import jakarta.servlet.http.HttpServletRequest;

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
	
	@ExceptionHandler(InvalidRecommendationRequestException.class)
	public ResponseEntity<ApiErrorResponse>
	handleInvalidRecommendationRequest(
	        InvalidRecommendationRequestException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.BAD_REQUEST.value(),
	                    "INVALID_RECOMMENDATION_REQUEST",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.BAD_REQUEST)
	            .body(error);
	}


	@ExceptionHandler(MlUserNotFoundException.class)
	public ResponseEntity<ApiErrorResponse>
	handleMlUserNotFound(
	        MlUserNotFoundException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.NOT_FOUND.value(),
	                    "ML_USER_NOT_FOUND",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.NOT_FOUND)
	            .body(error);
	}


	@ExceptionHandler(MlServiceUnavailableException.class)
	public ResponseEntity<ApiErrorResponse>
	handleMlServiceUnavailable(
	        MlServiceUnavailableException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.SERVICE_UNAVAILABLE.value(),
	                    "ML_SERVICE_UNAVAILABLE",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.SERVICE_UNAVAILABLE)
	            .body(error);
	}


	@ExceptionHandler(MlServiceException.class)
	public ResponseEntity<ApiErrorResponse>
	handleMlServiceError(
	        MlServiceException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.BAD_GATEWAY.value(),
	                    "ML_SERVICE_ERROR",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.BAD_GATEWAY)
	            .body(error);
	}


	@ExceptionHandler(MethodArgumentTypeMismatchException.class)
	public ResponseEntity<ApiErrorResponse>
	handleTypeMismatch(
	        MethodArgumentTypeMismatchException ex,
	        HttpServletRequest request
	) {

	    String message =
	            "Parameter '" + ex.getName()
	                    + "' must be a valid integer.";


	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.BAD_REQUEST.value(),
	                    "INVALID_PARAMETER_TYPE",
	                    message,
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.BAD_REQUEST)
	            .body(error);
	}
	
	@ExceptionHandler(UsernameAlreadyExistsException.class)
	public ResponseEntity<Map<String, Object>>
	handleUsernameAlreadyExists(
	        UsernameAlreadyExistsException ex) {

	    Map<String, Object> error = new HashMap<>();

	    error.put(
	            "status",
	            HttpStatus.CONFLICT.value()
	    );

	    error.put(
	            "message",
	            ex.getMessage()
	    );

	    return ResponseEntity
	            .status(HttpStatus.CONFLICT)
	            .body(error);
	}
	
	@ExceptionHandler(BadCredentialsException.class)
	public ResponseEntity<Map<String, Object>>
	handleBadCredentials(BadCredentialsException ex) {

	    Map<String, Object> error = new HashMap<>();

	    error.put(
	            "status",
	            HttpStatus.UNAUTHORIZED.value()
	    );

	    error.put(
	            "message",
	            "Invalid username or password"
	    );

	    return ResponseEntity
	            .status(HttpStatus.UNAUTHORIZED)
	            .body(error);
	}
	
	@ExceptionHandler(MovieAlreadyInCatalogException.class)
	public ResponseEntity<ApiErrorResponse>
	handleMovieAlreadyInCatalog(
	        MovieAlreadyInCatalogException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.CONFLICT.value(),
	                    "MOVIE_ALREADY_IN_CATALOG",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.CONFLICT)
	            .body(error);
	}
	
	@ExceptionHandler(UnsupportedMlMovieException.class)
	public ResponseEntity<ApiErrorResponse>
	handleUnsupportedMlMovie(
	        UnsupportedMlMovieException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.BAD_REQUEST.value(),
	                    "UNSUPPORTED_ML_MOVIE",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.BAD_REQUEST)
	            .body(error);
	}
	
	@ExceptionHandler(MlMovieNotFoundException.class)
	public ResponseEntity<ApiErrorResponse>
	handleMlMovieNotFound(
	        MlMovieNotFoundException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.NOT_FOUND.value(),
	                    "ML_MOVIE_NOT_FOUND",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.NOT_FOUND)
	            .body(error);
	}
	
	@ExceptionHandler(UserNotFoundException.class)
	public ResponseEntity<ApiErrorResponse>
	handleUserNotFound(
	        UserNotFoundException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.NOT_FOUND.value(),
	                    "USER_NOT_FOUND",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.NOT_FOUND)
	            .body(error);
	}
	
	@ExceptionHandler(AdminUserDeletionException.class)
	public ResponseEntity<ApiErrorResponse>
	handleAdminUserDeletion(
	        AdminUserDeletionException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.BAD_REQUEST.value(),
	                    "ADMIN_USER_DELETION_NOT_ALLOWED",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.BAD_REQUEST)
	            .body(error);
	}
	
	@ExceptionHandler(MovieInUseException.class)
	public ResponseEntity<ApiErrorResponse>
	handleMovieInUse(
	        MovieInUseException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.CONFLICT.value(),
	                    "MOVIE_IN_USE",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.CONFLICT)
	            .body(error);
	}
	
	@ExceptionHandler(InvalidMovieCatalogRequestException.class)
	public ResponseEntity<ApiErrorResponse>
	handleInvalidMovieCatalogRequest(
	        InvalidMovieCatalogRequestException ex,
	        HttpServletRequest request
	) {

	    ApiErrorResponse error =
	            new ApiErrorResponse(
	                    Instant.now(),
	                    HttpStatus.BAD_REQUEST.value(),
	                    "INVALID_MOVIE_CATALOG_REQUEST",
	                    ex.getMessage(),
	                    request.getRequestURI()
	            );

	    return ResponseEntity
	            .status(HttpStatus.BAD_REQUEST)
	            .body(error);
	}

}
