const AdminDashboard = {
    data() {
        return {
            activeTab: 'overview',
            stats: {},
            companies: [],
            drives: [],
            students: [],
            applications: [],
            searchText: '',
            error: ''
        };
    },
    async mounted() {
        this.loadOverview();
    },
    methods: {
        switchTab(tab) {
            this.activeTab = tab;
            this.error = '';
            if (tab === 'overview') this.loadOverview();
            if (tab === 'companies') this.loadCompanies();
            if (tab === 'drives') this.loadDrives();
            if (tab === 'students') this.loadStudents();
            if (tab === 'applications') this.loadApplications();
        },

        async loadOverview() {
            try { this.stats = await api.get('/admin/dashboard'); }
            catch (err) { this.error = err.message; }
        },

        async loadCompanies() {
            try { this.companies = await api.get('/admin/companies'); }
            catch (err) { this.error = err.message; }
        },
        async approveCompany(id) {
            await api.post(`/admin/approve_company/${id}`);
            this.loadCompanies();
        },
        async rejectCompany(id) {
            await api.post(`/admin/reject_company/${id}`);
            this.loadCompanies();
        },
        async blacklistCompany(id) {
            await api.post(`/admin/blacklist_company/${id}`);
            this.loadCompanies();
        },
        async searchCompanies() {
            this.companies = await api.get(`/admin/search_companies?name=${this.searchText}`);
        },

        async loadDrives() {
            try { this.drives = await api.get('/admin/drives'); }
            catch (err) { this.error = err.message; }
        },
        async approveDrive(id) {
            await api.post(`/admin/approve_drive/${id}`);
            this.loadDrives();
        },
        async rejectDrive(id) {
            await api.post(`/admin/reject_drive/${id}`);
            this.loadDrives();
        },
        async searchDrives() {
            this.drives = await api.get(`/admin/search_drives?title=${this.searchText}`);
        },

        async loadStudents() {
            try { this.students = await api.get('/admin/students'); }
            catch (err) { this.error = err.message; }
        },
        async deactivateUser(id) {
            await api.post(`/admin/deactivate_user/${id}`);
            this.loadStudents();
        },
        async activateUser(id) {
            await api.post(`/admin/activate_user/${id}`);
            this.loadStudents();
        },
        async searchStudents() {
            this.students = await api.get(`/admin/search_students?name=${this.searchText}`);
        },

        async loadApplications() {
            try { this.applications = await api.get('/admin/applications'); }
            catch (err) { this.error = err.message; }
        }
    },
    template: `
        <div>
            <h3 class="mb-3">Admin Dashboard</h3>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>

            <ul class="nav nav-tabs mb-3">
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='overview'}" href="#" @click.prevent="switchTab('overview')">Overview</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='companies'}" href="#" @click.prevent="switchTab('companies')">Companies</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='drives'}" href="#" @click.prevent="switchTab('drives')">Drives</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='students'}" href="#" @click.prevent="switchTab('students')">Students</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='applications'}" href="#" @click.prevent="switchTab('applications')">Applications</a></li>
            </ul>

            <!-- OVERVIEW TAB -->
            <div v-if="activeTab==='overview'" class="row g-3">
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.total_students }}</h2><small>Students</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.total_companies }}</h2><small>Companies</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.total_drives }}</h2><small>Drives</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.total_applications }}</h2><small>Applications</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.pending_companies }}</h2><small>Pending Companies</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.pending_drives }}</h2><small>Pending Drives</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h2>{{ stats.total_selected }}</h2><small>Selected</small></div></div>
            </div>

            <!-- COMPANIES TAB -->
            <div v-if="activeTab==='companies'">
                <div class="input-group mb-3" style="max-width:400px">
                    <input v-model="searchText" class="form-control" placeholder="Search company name">
                    <button class="btn btn-outline-secondary" @click="searchCompanies">Search</button>
                </div>
                <table class="table table-bordered">
                    <thead><tr><th>Name</th><th>HR Contact</th><th>Status</th><th>Blacklisted</th><th>Actions</th></tr></thead>
                    <tbody>
                        <tr v-for="c in companies" :key="c.id">
                            <td>{{ c.company_name }}</td>
                            <td>{{ c.hr_contact }}</td>
                            <td>{{ c.status }}</td>
                            <td>{{ c.is_blacklisted ? 'Yes' : 'No' }}</td>
                            <td>
                                <button class="btn btn-sm btn-success me-1" @click="approveCompany(c.id)">Approve</button>
                                <button class="btn btn-sm btn-warning me-1" @click="rejectCompany(c.id)">Reject</button>
                                <button class="btn btn-sm btn-dark" @click="blacklistCompany(c.id)">Blacklist</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- DRIVES TAB -->
            <div v-if="activeTab==='drives'">
                <div class="input-group mb-3" style="max-width:400px">
                    <input v-model="searchText" class="form-control" placeholder="Search drive title">
                    <button class="btn btn-outline-secondary" @click="searchDrives">Search</button>
                </div>
                <table class="table table-bordered">
                    <thead><tr><th>Job Title</th><th>Status</th><th>Deadline</th><th>Actions</th></tr></thead>
                    <tbody>
                        <tr v-for="d in drives" :key="d.id">
                            <td>{{ d.job_title }}</td>
                            <td>{{ d.status }}</td>
                            <td>{{ d.deadline }}</td>
                            <td>
                                <button class="btn btn-sm btn-success me-1" @click="approveDrive(d.id)">Approve</button>
                                <button class="btn btn-sm btn-warning" @click="rejectDrive(d.id)">Reject</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- STUDENTS TAB -->
            <div v-if="activeTab==='students'">
                <div class="input-group mb-3" style="max-width:400px">
                    <input v-model="searchText" class="form-control" placeholder="Search student name">
                    <button class="btn btn-outline-secondary" @click="searchStudents">Search</button>
                </div>
                <table class="table table-bordered">
                    <thead><tr><th>Name</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Active</th><th>Actions</th></tr></thead>
                    <tbody>
                        <tr v-for="s in students" :key="s.id">
                            <td>{{ s.name }}</td>
                            <td>{{ s.email }}</td>
                            <td>{{ s.branch }}</td>
                            <td>{{ s.cgpa }}</td>
                            <td>{{ s.is_active ? 'Yes' : 'No' }}</td>
                            <td>
                                <button v-if="s.is_active" class="btn btn-sm btn-warning" @click="deactivateUser(s.id)">Deactivate</button>
                                <button v-else class="btn btn-sm btn-success" @click="activateUser(s.id)">Activate</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- APPLICATIONS TAB -->
            <div v-if="activeTab==='applications'">
                <table class="table table-bordered">
                    <thead><tr><th>Student ID</th><th>Student Name</th><th>Drive ID</th><th>Job Title</th><th>Status</th><th>Application Date</th></tr></thead>
                    <tbody>
                        <tr v-for="a in applications" :key="a.id">
                            <td>{{ a.student_id }}</td>
                            <td>{{ a.student_name }}</td>
                            <td>{{ a.drive_id }}</td>
                            <td>{{ a.job_title }}</td>
                            <td>{{ a.status }}</td>
                            <td>{{ a.application_date }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `
};
