interface ApiFetchOptions extends RequestInit {
    token?: string;
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

export async function apiFetch<T = unknown>(
    url: string,
    options: ApiFetchOptions = {},
): Promise<T> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL as string | undefined;

    if (!apiUrl) {
        throw new Error("NEXT_PUBLIC_API_URL is not defined");
    }

    const { token, ...fetchOptions } = options;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(fetchOptions.headers as Record<string, string>),
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${apiUrl}${url}`, {
        ...fetchOptions,
        headers,
    });

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
    get: <T = unknown>(url: string, token?: string) =>
        apiFetch<T>(url, { method: "GET", token }),

    post: <T = unknown>(url: string, data?: unknown, token?: string) =>
        apiFetch<T>(url, {
            method: "POST",
            body: data ? JSON.stringify(data) : undefined,
            token,
        }),

    put: <T = unknown>(url: string, data: unknown, token?: string) =>
        apiFetch<T>(url, {
            method: "PUT",
            body: JSON.stringify(data),
            token,
        }),

    patch: <T = unknown>(url: string, data: unknown, token?: string) =>
        apiFetch<T>(url, {
            method: "PATCH",
            body: JSON.stringify(data),
            token,
        }),

    delete: <T = unknown>(url: string, token?: string) =>
        apiFetch<T>(url, { method: "DELETE", token }),
};

interface LoginCredentials {
    username: string;
    password: string;
}

interface User {
    id: string;
    username: string;
}

export async function login(credentials: LoginCredentials): Promise<void> {
    const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/login/token`,
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
    );

    if (!response.ok) {
        let errorData: { detail?: string } = {};
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
            try {
                errorData = await response.json();
            } catch {
                // Ignore parsing errors
            }
        }

        if (response.status === 401) {
            throw new Error("Incorrect username or password");
        }
        throw new Error(errorData.detail || "Login failed");
    }
}

export async function logout(): Promise<void> {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/logout`, {
        method: "POST",
        credentials: "include",
    });
}

export async function getCurrentUser(): Promise<User> {
    const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/login/me`,
        {
            credentials: "include",
        },
    );

    if (!response.ok) {
        throw new Error("Not authenticated");
    }

    return response.json();
}
