import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Users2, ShieldCheck, UserPlus, KeyRound, Building2, CheckCircle2, Trash2, Edit, Lock, Bot } from 'lucide-react';
import { ProvisioningPercentageLoader } from '../components/ProvisioningPercentageLoader';

interface UserAccount {
  user_id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  assigned_hotels?: string;
}

export const UsersManagement: React.FC = () => {
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserAccount | null>(null);

  // Form State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Revenue Manager');
  const [assignedHotels, setAssignedHotels] = useState('1'); // Default hotel ID
  const [successMsg, setSuccessMsg] = useState('');

  // Creation Percentage Loader State
  const [creatingUser, setCreatingUser] = useState(false);
  const [userProgress, setUserProgress] = useState(0);
  const [userStep, setUserStep] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAdminUsers();
      setUsers(data);
    } catch (err) {
      console.error('Failed to load user accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    let progressInterval: any = null;
    try {
      setCreatingUser(true);
      setUserProgress(10);
      setUserStep('Validating User Identity Credentials...');

      let currentPct = 10;
      progressInterval = setInterval(() => {
        currentPct += Math.floor(Math.random() * 4) + 3;
        if (currentPct > 90) currentPct = 90;
        setUserProgress(currentPct);

        if (currentPct < 30) {
          setUserStep('Encrypting Security Credentials...');
        } else if (currentPct < 60) {
          setUserStep(`Assigning '${role}' Access RBAC Matrix Scope...`);
        } else {
          setUserStep('Mapping Property Permissions & API Key Token...');
        }
      }, 60);

      await apiService.createAdminUser({
        email,
        password,
        full_name: fullName,
        role,
        assigned_hotels: assignedHotels,
      });

      if (progressInterval) clearInterval(progressInterval);
      setUserProgress(100);
      setUserStep('Account Created & Security Permissions Provisioned!');

      setTimeout(async () => {
        setSuccessMsg(`User '${fullName}' (${role}) created successfully!`);
        setShowAddModal(false);
        setEmail('');
        setPassword('');
        setFullName('');
        setCreatingUser(false);
        setUserProgress(0);
        await fetchUsers();
      }, 700);
    } catch (err: any) {
      if (progressInterval) clearInterval(progressInterval);
      console.error('Failed to create user:', err);
      setCreatingUser(false);
      setUserProgress(0);

      if (err?.response?.status !== 401) {
        const errMsg = err?.response?.data?.detail || err?.response?.data?.error?.message || 'Failed to create user. Check email format.';
        alert(errMsg);
      }
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await apiService.updateAdminUser(editingUser.user_id, {
        full_name: editingUser.full_name,
        role: editingUser.role,
        assigned_hotels: editingUser.assigned_hotels,
        is_active: editingUser.is_active,
      });
      setSuccessMsg(`Access updated for ${editingUser.full_name}`);
      setEditingUser(null);
      await fetchUsers();
    } catch (err) {
      console.error('Failed to update user access:', err);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('Are you sure you want to revoke and delete this user account?')) return;
    try {
      await apiService.deleteAdminUser(userId);
      setSuccessMsg('User account revoked successfully.');
      await fetchUsers();
    } catch (err) {
      console.error('Failed to delete user:', err);
    }
  };

  const rolesList = [
    'Super Admin',
    'Administrator',
    'Revenue Manager',
    'Hotel Manager',
    'Analyst',
    'Read-only User',
  ];

  return (
    <div className="space-y-8 font-sans">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-2xl shadow-lg shadow-indigo-600/30">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            Super Admin Access Control & Role Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Grant system roles, assign property permissions, and manage multi-tenant hotel revenue agents.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-5 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-bold rounded-2xl shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all hover:scale-[1.02]"
        >
          <UserPlus className="w-4 h-4" />
          Create New User & Grant Access
        </button>
      </div>

      {/* Hotel AI Agent Multi-Tenant Banner */}
      <div className="p-5 bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-900 border border-indigo-500/30 rounded-3xl space-y-2 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Hotel-Wise Multi-Tenant AI Agent Architecture</h3>
            <span className="px-2.5 py-0.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold rounded-full">
              AUTO-PROVISIONING ACTIVE
            </span>
          </div>
          <p className="text-xs text-slate-300">
            Currently running dedicated Revenue AI Agent for <strong className="text-white">Cute Orange Hotel</strong>. When a new hotel is added, a specialized AI Agent instance is automatically provisioned with custom compsets, forecasts, and guardrails!
          </p>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 text-xs font-bold flex items-center justify-between">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            {successMsg}
          </span>
          <button onClick={() => setSuccessMsg('')} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Users Accounts Table */}
      <div className="bg-slate-900/90 backdrop-blur border border-slate-800 rounded-3xl p-6 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Users2 className="w-5 h-5 text-indigo-400" />
            System User Accounts & Hotel Access Matrix
          </h3>
          <span className="text-xs text-slate-400 font-mono">
            Total Users: <strong className="text-white">{users.length}</strong>
          </span>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-bold">
                  <th className="pb-3 px-4">User</th>
                  <th className="pb-3 px-4">Email</th>
                  <th className="pb-3 px-4">Role Access</th>
                  <th className="pb-3 px-4">Assigned Hotel Scope</th>
                  <th className="pb-3 px-4">Status</th>
                  <th className="pb-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-white flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 text-white font-bold flex items-center justify-center text-xs">
                        {u.full_name.charAt(0)}
                      </div>
                      {u.full_name}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">{u.email}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2.5 py-1 text-[11px] rounded-full font-extrabold border ${
                          u.role === 'Super Admin'
                            ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                            : u.role === 'Administrator'
                            ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                            : u.role === 'Revenue Manager'
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                            : 'bg-slate-800 text-slate-300 border-slate-700'
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {u.role === 'Super Admin' || u.role === 'Administrator' || u.role === 'Revenue Manager'
                        ? '🌍 All Hotel Properties'
                        : `Hotel ID(s): ${u.assigned_hotels || '1'}`}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${u.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setEditingUser(u)}
                          className="p-1.5 text-slate-400 hover:text-indigo-400 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                          title="Edit Access"
                        >
                          <Edit className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u.user_id)}
                          className="p-1.5 text-slate-400 hover:text-rose-400 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                          title="Revoke Account"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* CREATE USER MODAL */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            {creatingUser ? (
              <ProvisioningPercentageLoader
                progress={userProgress}
                currentStep={userStep}
                title="Provisioning System User & Permissions..."
                subtitle={`Granting '${role}' RBAC access scope for ${fullName || 'User'}...`}
                steps={[
                  { label: "Validating User Identity & Credentials", minProgress: 20 },
                  { label: "Encrypting Security Passwords & Hashes", minProgress: 45 },
                  { label: `Assigning '${role}' Access RBAC Matrix`, minProgress: 70 },
                  { label: "Mapping Property Permissions & API Token", minProgress: 90 },
                  { label: "Account Provisioned & Security Keys Active", minProgress: 100 }
                ]}
              />
            ) : (
              <>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <UserPlus className="w-5 h-5 text-indigo-400" />
                  Create New User & Assign Permissions
                </h3>

                <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-bold">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-slate-300 font-bold">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. john@cuteorange.in"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-slate-300 font-bold">Account Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 8 characters..."
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-slate-300 font-bold">Assign Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                >
                  {rolesList.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-300 font-bold">Assigned Hotel Scope (IDs comma-separated)</label>
                <input
                  type="text"
                  value={assignedHotels}
                  onChange={(e) => setAssignedHotels(e.target.value)}
                  placeholder="e.g. 1 (Cute Orange Hotel) or 1,2,3"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                />
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  Create User
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  )}

      {/* EDIT USER MODAL */}
      {editingUser && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Edit className="w-5 h-5 text-indigo-400" />
              Modify User Role & Hotel Scope
            </h3>

            <form onSubmit={handleUpdateUser} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 font-bold">Full Name</label>
                <input
                  type="text"
                  value={editingUser.full_name}
                  onChange={(e) => setEditingUser({ ...editingUser, full_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                  required
                />
              </div>

              <div>
                <label className="text-slate-300 font-bold">Role</label>
                <select
                  value={editingUser.role}
                  onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                >
                  {rolesList.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-300 font-bold">Assigned Hotel Scope</label>
                <input
                  type="text"
                  value={editingUser.assigned_hotels || ''}
                  onChange={(e) => setEditingUser({ ...editingUser, assigned_hotels: e.target.value })}
                  placeholder="e.g. 1 or 1,2,3"
                  className="w-full bg-slate-950 border border-slate-800 text-white p-2.5 rounded-xl mt-1"
                />
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  Save Access Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
