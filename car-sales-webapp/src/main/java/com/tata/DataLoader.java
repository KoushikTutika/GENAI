package com.tata;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataLoader implements CommandLineRunner {
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        User user1 = new User();
        user1.setUsername("admin");
        user1.setPassword(passwordEncoder.encode("admin123"));
        user1.setRole("ADMIN");
        userRepository.save(user1);

        User user2 = new User();
        user2.setUsername("user");
        user2.setPassword(passwordEncoder.encode("user123"));
        user2.setRole("USER");
        userRepository.save(user2);
    }
}