package com.marshal.movierecommender.repository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.test.context.ActiveProfiles;

import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.entity.User;

@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(
        replace = AutoConfigureTestDatabase.Replace.NONE
)
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveUser() {

        User user = new User();
        user.setUsername("marshal_test");
        user.setPassword("test-password");
        user.setRole(Role.USER);

        User savedUser = userRepository.saveAndFlush(user);

        assertThat(savedUser.getId()).isNotNull();
        assertThat(savedUser.getUsername())
                .isEqualTo("marshal_test");
        assertThat(savedUser.getPassword())
                .isEqualTo("test-password");
        assertThat(savedUser.getRole())
                .isEqualTo(Role.USER);
    }

    @Test
    void shouldFindUserByUsername() {

        User user = new User();
        user.setUsername("find_user_test");
        user.setPassword("test-password");
        user.setRole(Role.USER);

        userRepository.saveAndFlush(user);

        Optional<User> result =
                userRepository.findByUsername("find_user_test");

        assertThat(result).isPresent();
        assertThat(result.get().getUsername())
                .isEqualTo("find_user_test");
        assertThat(result.get().getRole())
                .isEqualTo(Role.USER);
    }

    @Test
    void shouldCheckIfUsernameExists() {

        User user = new User();
        user.setUsername("existing_user_test");
        user.setPassword("test-password");
        user.setRole(Role.USER);

        userRepository.saveAndFlush(user);

        boolean exists =
                userRepository.existsByUsername(
                        "existing_user_test"
                );

        assertThat(exists).isTrue();
    }

    @Test
    void shouldRejectDuplicateUsername() {

        User firstUser = new User();
        firstUser.setUsername("duplicate_user_test");
        firstUser.setPassword("password-one");
        firstUser.setRole(Role.USER);

        userRepository.saveAndFlush(firstUser);

        User secondUser = new User();
        secondUser.setUsername("duplicate_user_test");
        secondUser.setPassword("password-two");
        secondUser.setRole(Role.USER);

        assertThatThrownBy(
                () -> userRepository.saveAndFlush(secondUser)
        ).isInstanceOf(DataIntegrityViolationException.class);
    }
}