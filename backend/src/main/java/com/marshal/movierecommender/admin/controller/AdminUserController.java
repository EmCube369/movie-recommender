package com.marshal.movierecommender.admin.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;

import com.marshal.movierecommender.admin.dto.AdminUserResponse;
import com.marshal.movierecommender.admin.service.AdminUserService;

@RestController
@RequestMapping("/api/admin/users")
public class AdminUserController {

    private final AdminUserService adminUserService;

    public AdminUserController(
            AdminUserService adminUserService
    ) {
        this.adminUserService = adminUserService;
    }


    @GetMapping
    public ResponseEntity<List<AdminUserResponse>>
    getAllUsers() {

        return ResponseEntity.ok(
                adminUserService.getAllUsers()
        );
    }


    @GetMapping("/{id}")
    public ResponseEntity<AdminUserResponse>
    getUserById(
            @PathVariable Integer id
    ) {

        return ResponseEntity.ok(
                adminUserService.getUserById(id)
        );
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(
            @PathVariable Integer id,
            Authentication authentication
    ) {

        adminUserService.deleteUser(
                id,
                authentication.getName()
        );

        return ResponseEntity
                .noContent()
                .build();
    }
    
}