const LoginPage = {
    data() {
        return {
            email: '',
            password: '',
            error: ''
        };
    },
    methods: {
        async handleLogin() {
            this.error = '';
            try {
                const data = await api.post('/auth/login', {
                    email: this.email,
                    password: this.password
                });

                
                authState.currentUser = {
                    user_id: data.user_id,
                    role: data.role,
                    name: data.name
                };

                
                if (data.role === 'admin') this.$router.push('/admin');
                else if (data.role === 'company') this.$router.push('/company');
                else this.$router.push('/student');

            } catch (err) {
                this.error = err.message;
            }
        }
    },
    template: `
        <div class="row justify-content-center mt-5">
            <div class="col-md-4">
                <h3 class="mb-3">Login</h3>
                <div v-if="error" class="alert alert-danger">{{ error }}</div>
                <form @submit.prevent="handleLogin">
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input v-model="email" type="email" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input v-model="password" type="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                <p class="mt-3 text-center">
                    New here? <router-link to="/register">Register as Student or Company</router-link>
                </p>
            </div>
        </div>
    `
};


const RegisterPage = {
    data() {
        return {
            name: '',
            email: '',
            password: '',
            role: 'student',
            error: '',
            success: ''
        };
    },
    methods: {
        async handleRegister() {
            this.error = '';
            this.success = '';
            try {
                await api.post('/auth/register', {
                    name: this.name,
                    email: this.email,
                    password: this.password,
                    role: this.role
                });
                this.success = 'Registration successful! You can login now.';
                setTimeout(() => this.$router.push('/login'), 1500);
            } catch (err) {
                this.error = err.message;
            }
        }
    },
    template: `
        <div class="row justify-content-center mt-5">
            <div class="col-md-4">
                <h3 class="mb-3">Register</h3>
                <div v-if="error" class="alert alert-danger">{{ error }}</div>
                <div v-if="success" class="alert alert-success">{{ success }}</div>
                <form @submit.prevent="handleRegister">
                    <div class="mb-3">
                        <label class="form-label">Full Name</label>
                        <input v-model="name" type="text" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input v-model="email" type="email" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input v-model="password" type="password" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">I am a</label>
                        <select v-model="role" class="form-select">
                            <option value="student">Student</option>
                            <option value="company">Company</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                </form>
                <p class="mt-3 text-center">
                    Already have an account? <router-link to="/login">Login</router-link>
                </p>
            </div>
        </div>
    `
};
