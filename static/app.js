const authState = Vue.reactive({
    currentUser: null
});


const routes = [
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage },
    { path: '/admin', component: AdminDashboard, meta: { role: 'admin' } },
    { path: '/company', component: CompanyDashboard, meta: { role: 'company' } },
    { path: '/student', component: StudentDashboard, meta: { role: 'student' } },
    { path: '/', redirect: '/login' }
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes: routes
});


router.beforeEach((to, from) => {
    const requiredRole = to.meta.role;
    if (requiredRole && (!authState.currentUser || authState.currentUser.role !== requiredRole)) {
        return '/login';
    }
    return true;
});


const app = Vue.createApp({
    data() {
        return {
            authState: authState   
        };
    },
    computed: {
        currentUser() {
            return this.authState.currentUser;
        }
    },
    methods: {
        async logout() {
            await api.get('/auth/logout');
            this.authState.currentUser = null;
            this.$router.push('/login');
        }
    },
    template: `
        <nav class="navbar navbar-dark bg-dark mb-4">
            <div class="container">
                <span class="navbar-brand">Placement Portal</span>
                <div v-if="currentUser" class="text-white">
                    {{ currentUser.name }} ({{ currentUser.role }})
                    <button class="btn btn-sm btn-outline-light ms-2" @click="logout">Logout</button>
                </div>
            </div>
        </nav>
        <div class="container">
            <router-view></router-view>
        </div>
    `
});

app.use(router);
app.mount('#app');
