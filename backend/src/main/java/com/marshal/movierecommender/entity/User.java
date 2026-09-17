package com.marshal.movierecommender.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

@Entity
@Table(
	name = "app_users",
	uniqueConstraints = {
		@UniqueConstraint(name = "uk_user_username", columnNames = "username")
	}
)
public class User {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Integer id;

	@NotBlank(message = "Username cannot be blank")
	@Size(min = 3, max = 50, message = "Username must be between 3 and 50 characters")
	@Column(nullable = false, length = 50)
	private String username;

	@NotBlank(message = "Password cannot be blank")
	@Column(nullable = false)
	private String password;

	@Enumerated(EnumType.STRING)
	@Column(nullable = false, length = 20)
	private Role role = Role.USER;

	public User() {
	}

	public User(Integer id, String username, String password, Role role) {
		this.id = id;
		this.username = username;
		this.password = password;
		this.role = role;
	}

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public Role getRole() {
		return role;
	}

	public void setRole(Role role) {
		this.role = role;
	}
}