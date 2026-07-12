const StudentDashboard = {
    data() {
        return {
            activeTab: 'profile',

            profile: {},
            cgpa: '', branch: '', year: '',
            resumeFile: null,
            profileMsg: '',

            drives: [],
            searchTitle: '',
            searchCompanyText: '',
            companies: [],
            applyMsg: '',

            applications: [],
            history: [],

            exportTaskId: '',
            exportStatus: '',
            exportResult: ''
        };
    },
    async mounted() {
        this.loadProfile();
    },
    methods: {
        switchTab(tab) {
            this.activeTab = tab;
            if (tab === 'profile') this.loadProfile();
            if (tab === 'drives') this.loadDrives();
            if (tab === 'applications') this.loadApplications();
            if (tab === 'history') this.loadHistory();
        },

        async loadProfile() {
            this.profile = await api.get('/student/profile');
            this.cgpa = this.profile.cgpa || '';
            this.branch = this.profile.branch || '';
            this.year = this.profile.year || '';
        },
        async updateProfile() {
            try {
                await api.post('/student/update_profile', {
                    cgpa: this.cgpa ? parseFloat(this.cgpa) : null,
                    branch: this.branch,
                    year: this.year ? parseInt(this.year) : null
                });
                this.profileMsg = 'Profile updated successfully';
                this.loadProfile();
            } catch (err) {
                this.profileMsg = err.message;
            }
        },
        onResumeSelected(event) {
            this.resumeFile = event.target.files[0];
        },
        async uploadResume() {
            if (!this.resumeFile) return;
            const formData = new FormData();
            formData.append('resume', this.resumeFile);

            const response = await fetch('/student/upload_resume', {
                method: 'POST',
                credentials: 'include',
                body: formData   
            });
            const data = await response.json();
            this.profileMsg = data.message;
            this.loadProfile();
        },

        async loadDrives() {
            this.drives = await api.get('/student/drives');
        },
        async searchDrives() {
            this.drives = await api.get(`/student/search_drives?title=${this.searchTitle}`);
        },
        async searchCompanies() {
            this.companies = await api.get(`/student/search_companies?name=${this.searchCompanyText}`);
        },
        async applyToDrive(driveId) {
            this.applyMsg = '';
            try {
                const data = await api.post('/student/apply', { drive_id: driveId });
                this.applyMsg = data.message;
            } catch (err) {
                this.applyMsg = err.message;
            }
        },

        async loadApplications() {
            this.applications = await api.get('/student/my_applications');
        },
        async loadHistory() {
            this.history = await api.get('/student/placement_history');
        },

        async startExport() {
            this.exportStatus = 'Starting...';
            const data = await api.get('/student/export');
            this.exportTaskId = data.task_id;
            this.pollExportStatus();
        },
        async pollExportStatus() {
            const data = await api.get(`/student/export_status/${this.exportTaskId}`);
            this.exportStatus = data.status;
            if (data.status === 'SUCCESS') {
                this.exportResult = data.result;
            } else if (data.status === 'PENDING' || data.status === 'STARTED') {
                setTimeout(() => this.pollExportStatus(), 1500);
            }
        },
        downloadCsv() {
            
            const filename = this.exportResult.split('/').pop();
            window.open(`/student/download_csv/${filename}`, '_blank');
        }
    },
    template: `
        <div>
            <h3 class="mb-3">Student Dashboard</h3>

            <ul class="nav nav-tabs mb-3">
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='profile'}" href="#" @click.prevent="switchTab('profile')">Profile</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='drives'}" href="#" @click.prevent="switchTab('drives')">Drives</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='applications'}" href="#" @click.prevent="switchTab('applications')">My Applications</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='history'}" href="#" @click.prevent="switchTab('history')">Placement History</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='export'}" href="#" @click.prevent="switchTab('export')">Export CSV</a></li>
            </ul>

            <!-- PROFILE TAB -->
            <div v-if="activeTab==='profile'" style="max-width:400px">
                <div v-if="profileMsg" class="alert alert-info">{{ profileMsg }}</div>
                <p><strong>Name:</strong> {{ profile.name }}</p>
                <p><strong>Email:</strong> {{ profile.email }}</p>
                <div class="mb-2">
                    <label class="form-label">CGPA</label>
                    <input v-model="cgpa" type="number" step="0.01" class="form-control">
                </div>
                <div class="mb-2">
                    <label class="form-label">Branch</label>
                    <input v-model="branch" class="form-control">
                </div>
                <div class="mb-2">
                    <label class="form-label">Year</label>
                    <input v-model="year" type="number" class="form-control">
                </div>
                <button class="btn btn-primary mb-3" @click="updateProfile">Save Profile</button>

                <div class="mb-2">
                    <label class="form-label">Resume (PDF only)</label>
                    <input type="file" accept=".pdf" class="form-control" @change="onResumeSelected">
                </div>
                <button class="btn btn-secondary" @click="uploadResume">Upload Resume</button>
                <p v-if="profile.resume" class="mt-2">Current resume: {{ profile.resume }}</p>
            </div>

            <!-- DRIVES TAB -->
            <div v-if="activeTab==='drives'">
                <div v-if="applyMsg" class="alert alert-info">{{ applyMsg }}</div>

                <div class="row mb-3">
                    <div class="col-md-4">
                        <div class="input-group">
                            <input v-model="searchTitle" class="form-control" placeholder="Search drive title">
                            <button class="btn btn-outline-secondary" @click="searchDrives">Search</button>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="input-group">
                            <input v-model="searchCompanyText" class="form-control" placeholder="Search company">
                            <button class="btn btn-outline-secondary" @click="searchCompanies">Search</button>
                        </div>
                    </div>
                </div>

                <div v-if="companies.length" class="mb-3">
                    <h6>Companies found:</h6>
                    <ul class="list-group" style="max-width:400px">
                        <li v-for="c in companies" :key="c.id" class="list-group-item">{{ c.company_name }} — {{ c.website }}</li>
                    </ul>
                </div>

                <table class="table table-bordered">
                    <thead><tr><th>Job Title</th><th>Company</th><th>Deadline</th><th>Eligibility</th><th>Min CGPA</th><th>Action</th></tr></thead>
                    <tbody>
                        <tr v-for="d in drives" :key="d.id">
                            <td>{{ d.job_title }}</td>
                            <td>{{ d.company }}</td>
                            <td>{{ d.deadline }}</td>
                            <td>{{ d.eligibility || 'Any' }}</td>
                            <td>{{ d.min_cgpa || '-' }}</td>
                            <td><button class="btn btn-sm btn-primary" @click="applyToDrive(d.id)">Apply</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- APPLICATIONS TAB -->
            <div v-if="activeTab==='applications'">
                <table class="table table-bordered">
                    <thead><tr><th>Job Title</th><th>Company</th><th>Status</th><th>Applied On</th><th>Interview</th></tr></thead>
                    <tbody>
                        <tr v-for="a in applications" :key="a.application_id">
                            <td>{{ a.job_title }}</td>
                            <td>{{ a.company }}</td>
                            <td>{{ a.status }}</td>
                            <td>{{ a.application_date }}</td>
                            <td>{{ a.interview_date || '-' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- HISTORY TAB -->
            <div v-if="activeTab==='history'">
                <table class="table table-bordered">
                    <thead><tr><th>Job Title</th><th>Company</th><th>Result</th><th>Applied On</th></tr></thead>
                    <tbody>
                        <tr v-for="h in history" :key="h.job_title + h.applied_on">
                            <td>{{ h.job_title }}</td>
                            <td>{{ h.company }}</td>
                            <td>{{ h.status }}</td>
                            <td>{{ h.applied_on }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- EXPORT TAB -->
            <div v-if="activeTab==='export'" style="max-width:400px">
                <button class="btn btn-primary mb-3" @click="startExport">Export My Applications as CSV</button>
                <p v-if="exportStatus">Status: <strong>{{ exportStatus }}</strong></p>
                <button v-if="exportStatus==='SUCCESS'" class="btn btn-success" @click="downloadCsv">Download CSV</button>
            </div>
        </div>
    `
};
