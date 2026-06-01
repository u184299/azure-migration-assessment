# --- Stage 1: Build Environment ---
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /src
COPY app/spring-petclinic/pom.xml .
# Cache dependencies before copying entire source tree
RUN mvn dependency:go-offline -B
COPY app/spring-petclinic/src ./src
RUN mvn package -DskipTests -B

# --- Stage 2: Secure Production Runtime ---
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# DevSecOps Hardening: Create an isolated non-root system account
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser

# Extract artifact from the compilation stage
COPY --from=build --chown=appuser:appgroup /src/target/*.jar app.jar

# Enforce secure runtime boundary context
USER appuser

EXPOSE 8080
ENV PORT=8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]