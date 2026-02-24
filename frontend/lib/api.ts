import { UserData } from "@/types/UserData";

interface ApiFetchOptions extends RequestInit {
    token?: string;
    maxRetries?: number;
    retryDelay?: number;
}

export class ApiError extends Error {
    constructor(
        public status: number,
        public statusText: string,
        public data?: unknown,
    ) {
        super(`API Error: ${status} ${statusText}`);
        this.name = "ApiError";
    }
}

async function fetchWithRetry(
    url: string,
    options: RequestInit,
    maxRetries: number = 3,
    baseDelay: number = 2000,
): Promise<Response> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetch(url, options);

            if (
                (response.status === 502 ||
                    response.status === 503 ||
                    response.status === 504) &&
                attempt < maxRetries
            ) {
                const delay = baseDelay * Math.pow(2, attempt);
                console.log(
                    `Server unavailable (${response.status}), retrying in ${delay}ms... (attempt ${attempt + 1}/${maxRetries})`,
                );
                await new Promise((resolve) => setTimeout(resolve, delay));
                continue;
            }

            return response;
        } catch (error) {
            lastError = error as Error;

            if (attempt < maxRetries) {
                const delay = baseDelay * Math.pow(2, attempt);
                console.log(
                    `Network error: ${(error as Error).message}, retrying in ${delay}ms... (attempt ${attempt + 1}/${maxRetries})`,
                );
                await new Promise((resolve) => setTimeout(resolve, delay));
                continue;
            }
        }
    }

    throw lastError || new Error("Max retries exceeded");
}

export async function apiFetch<T = unknown>(
    url: string,
    options: ApiFetchOptions = {},
): Promise<T> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL as string | undefined;

    if (!apiUrl) {
        throw new Error("NEXT_PUBLIC_API_URL is not defined");
    }

    const {
        token,
        maxRetries = 3,
        retryDelay = 2000,
        ...fetchOptions
    } = options;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(fetchOptions.headers as Record<string, string>),
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetchWithRetry(
        `${apiUrl}${url}`,
        {
            ...fetchOptions,
            headers,
            credentials: "include",
        },
        maxRetries,
        retryDelay,
    );

    if (!response.ok) {
        let errorData;
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
            try {
                errorData = await response.json();
            } catch {
                errorData = "Failed to parse error response";
            }
        } else {
            try {
                errorData = await response.text();
            } catch {
                errorData = "Failed to read error response";
            }
        }

        throw new ApiError(response.status, response.statusText, errorData);
    }

    if (response.status === 204) {
        return null as T;
    }

    return response.json();
}

export const api = {
    get: <T = unknown>(url: string, token?: string, maxRetries?: number) =>
        apiFetch<T>(url, { method: "GET", token, maxRetries }),

    post: <T = unknown>(
        url: string,
        data?: unknown,
        token?: string,
        maxRetries?: number,
    ) =>
        apiFetch<T>(url, {
            method: "POST",
            body: data ? JSON.stringify(data) : undefined,
            token,
            maxRetries,
        }),

    put: <T = unknown>(
        url: string,
        data: unknown,
        token?: string,
        maxRetries?: number,
    ) =>
        apiFetch<T>(url, {
            method: "PUT",
            body: JSON.stringify(data),
            token,
            maxRetries,
        }),

    patch: <T = unknown>(
        url: string,
        data: unknown,
        token?: string,
        maxRetries?: number,
    ) =>
        apiFetch<T>(url, {
            method: "PATCH",
            body: JSON.stringify(data),
            token,
            maxRetries,
        }),

    delete: <T = unknown>(url: string, token?: string, maxRetries?: number) =>
        apiFetch<T>(url, { method: "DELETE", token, maxRetries }),
};

interface LoginCredentials {
    username: string;
    password: string;
}

export async function login(credentials: LoginCredentials): Promise<void> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!apiUrl) {
        throw new Error("NEXT_PUBLIC_API_URL is not defined");
    }

    const response = await fetchWithRetry(
        `${apiUrl}/login/token`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(
                credentials as unknown as Record<string, string>,
            ),
            credentials: "include",
        },
        3,
        3000,
    );

    if (!response.ok) {
        let errorData: { detail?: string } = {};
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
            try {
                errorData = await response.json();
            } catch {}
        }

        if (response.status === 401) {
            throw new Error("Incorrect username or password");
        }
        throw new Error(errorData.detail || "Login failed");
    }
}

export async function logout(): Promise<void> {
    return api.post("/logout", undefined, undefined, 0);
}

export async function getCurrentUser(): Promise<UserData> {
    return api.get<UserData>("/login/me", undefined, 0);
}
