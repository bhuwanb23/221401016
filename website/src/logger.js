/**
 * Logging Middleware for Frontend
 * Sends logs to the evaluation service with proper validation and error handling
 */

class LoggingMiddleware {
    constructor(apiUrl = "http://20.244.56.144/evaluation-service/logs") {
        this.apiUrl = apiUrl;
        
        // Valid values for validation
        this.validStacks = new Set(["backend", "frontend"]);
        this.validLevels = new Set(["debug", "info", "warn", "error", "fatal"]);
        this.validBackendPackages = new Set([
            "cache", "controller", "cron_job", "db", "domain", 
            "handler", "respoistory", "route", "service"
        ]);
        this.validFrontendPackages = new Set([
            "api", "components", "hooks", "page", "state", "style"
        ]);
        this.validSharedPackages = new Set([
            "auth", "config", "middleware", "utils"
        ]);
        
        // Setup local logging for debugging
        this.setupLocalLogging();
    }
    
    setupLocalLogging() {
        // Create a simple local logger for debugging
        this.localLogger = {
            info: (message, data) => console.log(`[INFO] ${message}`, data),
            error: (message, data) => console.error(`[ERROR] ${message}`, data),
            warn: (message, data) => console.warn(`[WARN] ${message}`, data),
            debug: (message, data) => console.debug(`[DEBUG] ${message}`, data)
        };
    }
    
    validateStack(stack) {
        if (!this.validStacks.has(stack.toLowerCase())) {
            this.localLogger.error(`Invalid stack: ${stack}. Valid values: ${Array.from(this.validStacks).join(', ')}`);
            return false;
        }
        return true;
    }
    
    validateLevel(level) {
        if (!this.validLevels.has(level.toLowerCase())) {
            this.localLogger.error(`Invalid level: ${level}. Valid values: ${Array.from(this.validLevels).join(', ')}`);
            return false;
        }
        return true;
    }
    
    validatePackage(package, stack) {
        const packageLower = package.toLowerCase();
        let validPackages;
        
        if (stack.toLowerCase() === "backend") {
            validPackages = new Set([...this.validBackendPackages, ...this.validSharedPackages]);
        } else if (stack.toLowerCase() === "frontend") {
            validPackages = new Set([...this.validFrontendPackages, ...this.validSharedPackages]);
        } else {
            this.localLogger.error(`Invalid stack for package validation: ${stack}`);
            return false;
        }
        
        if (!validPackages.has(packageLower)) {
            this.localLogger.error(`Invalid package '${package}' for stack '${stack}'. Valid packages: ${Array.from(validPackages).join(', ')}`);
            return false;
        }
        return true;
    }
    
    formatMessage(message, context = {}) {
        if (Object.keys(context).length === 0) {
            return message;
        }
        
        const contextStr = Object.entries(context)
            .map(([key, value]) => `${key}=${value}`)
            .join(' | ');
        
        return `${message} | Context: ${contextStr}`;
    }
    
    async log(stack, level, package, message, context = {}) {
        try {
            // Validate inputs
            if (!this.validateStack(stack)) {
                return null;
            }
            if (!this.validateLevel(level)) {
                return null;
            }
            if (!this.validatePackage(package, stack)) {
                return null;
            }
            
            // Format message with context
            const formattedMessage = this.formatMessage(message, context);
            
            // Prepare request payload
            const payload = {
                stack: stack.toLowerCase(),
                level: level.toLowerCase(),
                package: package.toLowerCase(),
                message: formattedMessage
            };
            
            // Make API call
            const startTime = performance.now();
            
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            const elapsedTime = performance.now() - startTime;
            
            // Log the API call locally for debugging
            this.localLogger.info(`Log API call - Status: ${response.status}, Time: ${elapsedTime.toFixed(3)}ms`);
            
            if (response.status === 200) {
                const responseData = await response.json();
                this.localLogger.info(`Log created successfully - ID: ${responseData.logID || 'N/A'}`);
                return responseData;
            } else {
                const errorText = await response.text();
                this.localLogger.error(`Log API failed - Status: ${response.status}, Response: ${errorText}`);
                return null;
            }
            
        } catch (error) {
            this.localLogger.error(`Log API request failed: ${error.message}`);
            return null;
        }
    }
    
    async debug(stack, package, message, context = {}) {
        return this.log(stack, "debug", package, message, context);
    }
    
    async info(stack, package, message, context = {}) {
        return this.log(stack, "info", package, message, context);
    }
    
    async warn(stack, package, message, context = {}) {
        return this.log(stack, "warn", package, message, context);
    }
    
    async error(stack, package, message, context = {}) {
        return this.log(stack, "error", package, message, context);
    }
    
    async fatal(stack, package, message, context = {}) {
        return this.log(stack, "fatal", package, message, context);
    }
}

// Global logger instance
const logger = new LoggingMiddleware();

// Convenience functions for easy usage
export const Log = async (stack, level, package, message, context = {}) => {
    return logger.log(stack, level, package, message, context);
};

export const logDebug = async (stack, package, message, context = {}) => {
    return logger.debug(stack, package, message, context);
};

export const logInfo = async (stack, package, message, context = {}) => {
    return logger.info(stack, package, message, context);
};

export const logWarn = async (stack, package, message, context = {}) => {
    return logger.warn(stack, package, message, context);
};

export const logError = async (stack, package, message, context = {}) => {
    return logger.error(stack, package, message, context);
};

export const logFatal = async (stack, package, message, context = {}) => {
    return logger.fatal(stack, package, message, context);
};

// Export the logger instance for advanced usage
export { logger as LoggingMiddleware };

// React Hook for logging
export const useLogger = () => {
    return {
        log: Log,
        debug: logDebug,
        info: logInfo,
        warn: logWarn,
        error: logError,
        fatal: logFatal
    };
}; 