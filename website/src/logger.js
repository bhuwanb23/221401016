/**
 * Logging Middleware for Frontend
 * Sends logs to the evaluation service with proper validation and error handling
 */

class LoggingMiddleware {
    constructor(apiUrl = "http://20.244.56.144/evaluation-service/logs") {
        this.apiUrl = apiUrl;
        
        // Authorization token
        this.authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiIyMjE0MDEwMTZAcmFqYWxha3NobWkuZWR1LmluIiwiZXhwIjoxNzUxNjk3NDg4LCJpYXQiOjE3NTE2OTY4ODgsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxZDU4YmFlOC01NWM2LTQ4M2UtOTcwMy1lMDc1MWE5MmY2YzIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJiaHV3YW4gYiIsInN1YiI6ImZkNjNmNmI0LTkzNjYtNGVlZS1hMTk2LTM1OTFmNzE1MDkxOCJ9LCJlbWFpbCI6IjIyMTQwMTAxNkByYWphbGFrc2htaS5lZHUuaW4iLCJuYW1lIjoiYmh1d2FuIGIiLCJyb2xsTm8iOiIyMjE0MDEwMTYiLCJhY2Nlc3NDb2RlIjoiY1d5YVhXIiwiY2xpZW50SUQiOiJmZDYzZjZiNC05MzY2LTRlZWUtYTE5Ni0zNTkxZjcxNTA5MTgiLCJjbGllbnRTZWNyZXQiOiJRR05XWndyZXpFakRiWlFnIn0.LWvv_mMUa4a5fM7uaLB3mB9ow8INSc";
        
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
    
    validatePackage(packageName, stack) {
        const packageLower = packageName.toLowerCase();
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
            this.localLogger.error(`Invalid package '${packageName}' for stack '${stack}'. Valid packages: ${Array.from(validPackages).join(', ')}`);
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
    
    async log(stack, level, packageName, message, context = {}) {
        try {
            // Validate inputs
            if (!this.validateStack(stack)) {
                return null;
            }
            if (!this.validateLevel(level)) {
                return null;
            }
            if (!this.validatePackage(packageName, stack)) {
                return null;
            }
            
            // Format message with context
            const formattedMessage = this.formatMessage(message, context);
            
            // Prepare request payload
            const payload = {
                stack: stack.toLowerCase(),
                level: level.toLowerCase(),
                package: packageName.toLowerCase(),
                message: formattedMessage
            };
            
            // Make API call
            const startTime = performance.now();
            
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
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
    
    async debug(stack, packageName, message, context = {}) {
        return this.log(stack, "debug", packageName, message, context);
    }
    
    async info(stack, packageName, message, context = {}) {
        return this.log(stack, "info", packageName, message, context);
    }
    
    async warn(stack, packageName, message, context = {}) {
        return this.log(stack, "warn", packageName, message, context);
    }
    
    async error(stack, packageName, message, context = {}) {
        return this.log(stack, "error", packageName, message, context);
    }
    
    async fatal(stack, packageName, message, context = {}) {
        return this.log(stack, "fatal", packageName, message, context);
    }
}

// Global logger instance
const logger = new LoggingMiddleware();

// Convenience functions for easy usage
export const Log = async (stack, level, packageName, message, context = {}) => {
    return logger.log(stack, level, packageName, message, context);
};

export const logDebug = async (stack, packageName, message, context = {}) => {
    return logger.debug(stack, packageName, message, context);
};

export const logInfo = async (stack, packageName, message, context = {}) => {
    return logger.info(stack, packageName, message, context);
};

export const logWarn = async (stack, packageName, message, context = {}) => {
    return logger.warn(stack, packageName, message, context);
};

export const logError = async (stack, packageName, message, context = {}) => {
    return logger.error(stack, packageName, message, context);
};

export const logFatal = async (stack, packageName, message, context = {}) => {
    return logger.fatal(stack, packageName, message, context);
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