// API Wrapper
class API {
    static getHeaders() {
        // In a real app with token auth, add Authorization header here
        return {
            'Content-Type': 'application/json',
            // 'Authorization': `Token ${localStorage.getItem('token')}`
        };
    }

    static async fetchGyms(lat = null, lon = null) {
        let url = `${config.API_URL}/gyms/`;
        if (lat && lon) {
            url += `?lat=${lat}&lon=${lon}`;
        }

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch gyms');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return [];
        }
    }

    static async getGymDetail(id) {
        try {
            const response = await fetch(`${config.API_URL}/gyms/${id}/`);
            if (!response.ok) throw new Error('Gym not found');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    static async login(username, password) {
        try {
            const response = await fetch(`${config.API_URL}/login/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ username, password })
            });
            return await response.json();
        } catch (error) {
            console.error('Login Error:', error);
            return { error: 'Network error' };
        }
    }

    static async getOwnerDashboard() {
        try {
            const response = await fetch(`${config.API_URL}/owner/dashboard/`, {
                headers: this.getHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch dashboard');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    static async googleLogin(token, role = null) {
        try {
            const body = { token };
            if (role) body.role = role;

            const response = await fetch(`${config.API_URL}/auth/google/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(body)
            });
            return await response.json();
        } catch (error) {
            console.error('Google Login Error:', error);
            return { error: 'Network error' };
        }
    }

    static async registerCustomer(data) {
        try {
            const response = await fetch(`${config.API_URL}/register/customer/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Registration Error:', error);
            return { error: 'Network error' };
        }
    }

    static async registerOwner(data) {
        try {
            const response = await fetch(`${config.API_URL}/register/owner/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Registration Error:', error);
            return { error: 'Network error' };
        }
    }

    static async createGym(data) {
        try {
            const response = await fetch(`${config.API_URL}/gyms/create/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Gym Creation Error:', error);
            return { error: 'Network error' };
        }
    }

    static async createPlan(gymId, data) {
        try {
            const response = await fetch(`${config.API_URL}/gyms/${gymId}/plans/create/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Plan Creation Error:', error);
            return { error: 'Network error' };
        }
    }
}
