const CompanyDashboard = {
    data() {
        return {
            activeTab: 'profile',
            profile: null,
            profileError: '',
            newCompanyName: '',
            newHrContact: '',
            newWebsite: '',

            drives: [],
            newJobTitle: '',
            newDescription: '',
            newEligibility: '',
            newMinCgpa: '',
            newMinYear: '',
            newDeadline: '',
            driveError: '',

            selectedDriveId: null,
            applicants: [],
            newInterviewDate: ''
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
        },

        async loadProfile() {
            try {
                this.profile = await api.get('/company/profile');
                this.profileError = '';
            } catch (err) {
                this.profile = null;
                this.profileError = err.message;
            }
        },
        async createProfile() {
            try {
                await api.post('/company/create_profile', {
                    company_name: this.newCompanyName,
                    hr_contact: this.newHrContact,
                    website: this.newWebsite
                });
                this.loadProfile();
            } catch (err) {
                this.profileError = err.message;
            }
        },

        async loadDrives() {
            try { this.drives = await api.get('/company/my_drives'); }
            catch (err) { this.driveError = err.message; }
        },
        async createDrive() {
            this.driveError = '';
            try {
                await api.post('/company/create_drive', {
                    job_title: this.newJobTitle,
                    description: this.newDescription,
                    eligibility: this.newEligibility,
                    min_cgpa: this.newMinCgpa ? parseFloat(this.newMinCgpa) : null,
                    min_year: this.newMinYear ? parseInt(this.newMinYear) : null,
                    deadline: this.newDeadline
                });
                this.newJobTitle = ''; this.newDescription = ''; this.newEligibility = '';
                this.newMinCgpa = ''; this.newMinYear = ''; this.newDeadline = '';
                this.loadDrives();
            } catch (err) {
                this.driveError = err.message;
            }
        },
        async closeDrive(id) {
            await api.post(`/company/close_drive/${id}`);
            this.loadDrives();
        },

        async viewApplicants(driveId) {
            this.selectedDriveId = driveId;
            this.applicants = await api.get(`/company/applications/${driveId}`);
        },
        async updateStatus(appId, status) {
            await api.post(`/company/update_application/${appId}`, { status: status });
            this.viewApplicants(this.selectedDriveId);
        },
        async scheduleInterview(appId) {
            if (!this.newInterviewDate) return;
            await api.post(`/company/schedule_interview/${appId}`, { interview_date: this.newInterviewDate });
            this.viewApplicants(this.selectedDriveId);
        }
    },
    template: `
        <div>
            <h3 class="mb-3">Company Dashboard</h3>

            <ul class="nav nav-tabs mb-3">
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='profile'}" href="#" @click.prevent="switchTab('profile')">Profile</a></li>
                <li class="nav-item"><a class="nav-link" :class="{active: activeTab==='drives'}" href="#" @click.prevent="switchTab('drives')">My Drives</a></li>
            </ul>

            <!-- PROFILE TAB -->
            <div v-if="activeTab==='profile'">
                <div v-if="profile" class="card p-3" style="max-width:500px">
                    <p><strong>Company:</strong> {{ profile.company_name }}</p>
                    <p><strong>HR Contact:</strong> {{ profile.hr_contact }}</p>
                    <p><strong>Website:</strong> {{ profile.website }}</p>
                    <p><strong>Status:</strong> {{ profile.status }}</p>
                </div>
                <div v-else style="max-width:400px">
                    <div v-if="profileError" class="alert alert-info">{{ profileError }}</div>
                    <h5>Create Company Profile</h5>
                    <div class="mb-2"><input v-model="newCompanyName" class="form-control" placeholder="Company Name"></div>
                    <div class="mb-2"><input v-model="newHrContact" class="form-control" placeholder="HR Contact Email"></div>
                    <div class="mb-2"><input v-model="newWebsite" class="form-control" placeholder="Website (optional)"></div>
                    <button class="btn btn-primary" @click="createProfile">Create Profile</button>
                </div>
            </div>

            <!-- DRIVES TAB -->
            <div v-if="activeTab==='drives'">
                <div v-if="driveError" class="alert alert-danger">{{ driveError }}</div>

                <div class="card p-3 mb-4" style="max-width:500px">
                    <h5>Create New Drive</h5>
                    <div class="mb-2"><input v-model="newJobTitle" class="form-control" placeholder="Job Title"></div>
                    <div class="mb-2"><textarea v-model="newDescription" class="form-control" placeholder="Description"></textarea></div>
                    <div class="mb-2"><input v-model="newEligibility" class="form-control" placeholder="Eligible Branches (e.g. CSE,IT)"></div>
                    <div class="mb-2"><input v-model="newMinCgpa" type="number" step="0.1" class="form-control" placeholder="Minimum CGPA"></div>
                    <div class="mb-2"><input v-model="newMinYear" type="number" class="form-control" placeholder="Minimum Year"></div>
                    <div class="mb-2">
                        <label class="form-label">Deadline</label>
                        <input v-model="newDeadline" type="date" class="form-control">
                    </div>
                    <button class="btn btn-primary" @click="createDrive">Create Drive</button>
                </div>

                <table class="table table-bordered">
                    <thead><tr><th>Job Title</th><th>Status</th><th>Deadline</th><th>Applicants</th><th>Actions</th></tr></thead>
                    <tbody>
                        <tr v-for="d in drives" :key="d.id">
                            <td>{{ d.job_title }}</td>
                            <td>{{ d.status }}</td>
                            <td>{{ d.deadline }}</td>
                            <td>{{ d.applicant_count }}</td>
                            <td>
                                <button class="btn btn-sm btn-info me-1" @click="viewApplicants(d.id)">View Applicants</button>
                                <button v-if="d.status !== 'Closed'" class="btn btn-sm btn-secondary" @click="closeDrive(d.id)">Close</button>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <!-- APPLICANTS FOR SELECTED DRIVE -->
                <div v-if="selectedDriveId" class="mt-4">
                    <h5>Applicants for Drive #{{ selectedDriveId }}</h5>
                    <table class="table table-bordered">
                        <thead><tr><th>Name</th><th>Email</th><th>CGPA</th><th>Branch</th><th>Status</th><th>Interview</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="a in applicants" :key="a.application_id">
                                <td>{{ a.student_name }}</td>
                                <td>{{ a.student_email }}</td>
                                <td>{{ a.cgpa }}</td>
                                <td>{{ a.branch }}</td>
                                <td>{{ a.status }}</td>
                                <td>{{ a.interview_date || '-' }}</td>
                                <td>
                                    <select class="form-select form-select-sm mb-1" @change="updateStatus(a.application_id, $event.target.value)">
                                        <option disabled selected>Set status</option>
                                        <option>Shortlisted</option>
                                        <option>Selected</option>
                                        <option>Rejected</option>
                                    </select>
                                    <div class="input-group input-group-sm">
                                        <input v-model="newInterviewDate" type="datetime-local" class="form-control">
                                        <button class="btn btn-outline-secondary" @click="scheduleInterview(a.application_id)">Set</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `
};
