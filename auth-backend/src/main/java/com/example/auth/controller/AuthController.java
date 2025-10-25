package com.example.auth.controller;

import com.example.auth.model.User;
import com.example.auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    @Autowired
    private UserRepository userRepository;

    // Регистрация
    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody User user) {
        try {
            // Проверяем, есть ли уже пользователь с таким именем
            if (userRepository.findByUsername(user.getUsername()).isPresent()) {
                Map<String, String> response = new HashMap<>();
                response.put("message", "Пользователь с таким именем уже существует");
                return ResponseEntity.badRequest().body(response);
            }

            // Сохраняем пользователя
            User savedUser = userRepository.save(user);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Пользователь успешно зарегистрирован");
            response.put("userId", savedUser.getId().toString());
            response.put("redirectUrl", "http://localhost:3000?user=" + savedUser.getUsername());
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> response = new HashMap<>();
            response.put("message", "Ошибка при регистрации: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    // Вход
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody User loginRequest) {
        try {
            Optional<User> user = userRepository.findByUsernameAndPassword(
                    loginRequest.getUsername(),
                    loginRequest.getPassword()
            );

            if (user.isPresent()) {
                Map<String, String> response = new HashMap<>();
                response.put("message", "Вход выполнен успешно");
                response.put("userId", user.get().getId().toString());
                response.put("username", user.get().getUsername());
                response.put("redirectUrl", "http://localhost:3000?user=" + user.get().getUsername());
                return ResponseEntity.ok(response);
            } else {
                Map<String, String> response = new HashMap<>();
                response.put("message", "Неверное имя пользователя или пароль");
                return ResponseEntity.badRequest().body(response);
            }

        } catch (Exception e) {
            Map<String, String> response = new HashMap<>();
            response.put("message", "Ошибка при входе: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    // Простой endpoint для проверки работы
    @GetMapping("/test")
    public String test() {
        return "Auth service is working!";
    }
}