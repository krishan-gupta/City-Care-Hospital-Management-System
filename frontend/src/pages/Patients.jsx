import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit2, Trash2, GitFork, User, ShieldCheck } from 'lucide-react';
import { getPatients, createPatient, updatePatient, deletePatient } from '../api';
import Table from '../components/Table';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import FormField from '../components/FormField';
import ErrorBanner from '../components/ErrorBanner';

export default function Patients() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    dob: '',
    gender: 'M',
    phone: '',
    address: '',
    bloodGroup: '',
    companyId: 'WellnessCorp',
    policyNo: ''
  });

  const fetchPatients = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getPatients({ search, page, size: 10 });
      setPatients(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to fetch patients.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [page, search]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleOpenAdd = () => {
    setFormData({
      name: '',
      dob: '1990-01-01',
      gender: 'M',
      phone: '',
      address: '',
      bloodGroup: 'O+',
      companyId: 'WellnessCorp',
      policyNo: 'INS-' + Math.floor(100000 + Math.random() * 900000)
    });
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (p) => {
    setSelectedPatient(p);
    setFormData({
      name: p.name || `${p.firstName || ''} ${p.lastName || ''}`.strip(),
      dob: p.dob ? String(p.dob).substring(0, 10) : '',
      gender: p.gender || 'M',
      phone: p.phone || '',
      address: p.address || '',
      bloodGroup: p.bloodGroup || '',
      companyId: p.insuranceCompany || '',
      policyNo: p.policyNo || ''
    });
    setIsEditModalOpen(true);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createPatient(formData);
      setIsAddModalOpen(false);
      fetchPatients();
    } catch (err) {
      alert(`Error creating patient: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!selectedPatient) return;
    setIsSubmitting(true);
    try {
      await updatePatient(selectedPatient.patientId, formData);
      setIsEditModalOpen(false);
      fetchPatients();
    } catch (err) {
      alert(`Error updating patient: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setIsSubmitting(true);
    try {
      await deletePatient(deleteId);
      setDeleteId(null);
      fetchPatients();
    } catch (err) {
      alert(`Error deleting patient: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'patientId',
      render: (r) => (
        <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
          {r.patientId}
        </span>
      )
    },
    {
      header: 'Patient Name',
      accessor: 'name',
      render: (r) => (
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs">
            {r.name?.charAt(0) || 'P'}
          </div>
          <div>
            <span className="font-semibold text-slate-900 block">{r.name}</span>
            <span className="text-xs text-slate-400">{r.gender === 'M' ? 'Male' : r.gender === 'F' ? 'Female' : r.gender}</span>
          </div>
        </div>
      )
    },
    {
      header: 'Age (Derived)',
      accessor: 'age',
      render: (r) => (
        <span className="font-medium text-slate-700">
          {r.age !== null && r.age !== undefined ? `${r.age} yrs` : '—'}
        </span>
      )
    },
    {
      header: 'Contact',
      accessor: 'phone',
      render: (r) => (
        <div>
          <span className="text-slate-800 text-xs block font-medium">{r.phone || '—'}</span>
          <span className="text-slate-400 text-xs truncate max-w-[140px] block">{r.address || '—'}</span>
        </div>
      )
    },
    {
      header: 'Insurance',
      accessor: 'insuranceCompany',
      render: (r) => (
        r.insuranceCompany ? (
          <div className="flex items-center space-x-1 text-xs text-slate-600 bg-sky-50 border border-sky-100 px-2.5 py-1 rounded-lg w-max">
            <ShieldCheck className="w-3.5 h-3.5 text-sky-600" />
            <span className="font-medium text-sky-800">{r.insuranceCompany}</span>
          </div>
        ) : (
          <span className="text-xs text-slate-400">Direct Pay</span>
        )
      )
    },
    {
      header: 'Actions',
      align: 'right',
      render: (r) => (
        <div className="flex items-center justify-end space-x-1.5">
          <button
            onClick={() => navigate(`/patients/${r.patientId}/journey`)}
            title="View Patient Journey Graph"
            className="p-1.5 text-emerald-600 hover:text-emerald-800 hover:bg-emerald-50 rounded-lg transition-colors flex items-center space-x-1 text-xs font-semibold"
          >
            <GitFork className="w-4 h-4" />
            <span className="hidden md:inline">Journey</span>
          </button>
          <button
            onClick={() => handleOpenEdit(r)}
            title="Edit Patient"
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setDeleteId(r.patientId)}
            title="Delete Patient & Subgraph"
            className="p-1.5 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Patients Directory</h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse registered patients, derived age calculations, insurance, and medical graph histories.
          </p>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={fetchPatients} />

      <Table
        columns={columns}
        data={patients}
        searchValue={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        searchPlaceholder="Search patients by name, phone, or ID..."
        currentPage={page}
        totalPages={Math.ceil(total / 10)}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyMessage="No patients found matching your search."
        actionButton={
          <button
            onClick={handleOpenAdd}
            className="flex items-center space-x-1.5 px-4 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition-colors shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Add Patient</span>
          </button>
        }
      />

      {/* Add Patient Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Register New Patient"
        subtitle="Creates a new :Patient node in Neo4j with personal and insurance details."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g. David Williams"
              required
            />
            <FormField
              label="Date of Birth"
              name="dob"
              type="date"
              value={formData.dob}
              onChange={handleInputChange}
              required
              helperText="Age will be derived dynamically in Cypher queries"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Gender"
              name="gender"
              type="select"
              value={formData.gender}
              onChange={handleInputChange}
              options={[
                { value: 'M', label: 'Male' },
                { value: 'F', label: 'Female' },
                { value: 'Other', label: 'Other' }
              ]}
              required
            />
            <FormField
              label="Phone Number"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              placeholder="e.g. 9876543210"
              required
            />
          </div>

          <FormField
            label="Address"
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            placeholder="Street address, city"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Insurance Provider"
              name="companyId"
              type="select"
              value={formData.companyId}
              onChange={handleInputChange}
              options={[
                { value: 'WellnessCorp', label: 'WellnessCorp' },
                { value: 'PulseSecure', label: 'PulseSecure' },
                { value: 'CarePlus', label: 'CarePlus' }
              ]}
            />
            <FormField
              label="Policy / Card Number"
              name="policyNo"
              value={formData.policyNo}
              onChange={handleInputChange}
              placeholder="e.g. INS-840674"
            />
          </div>

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsAddModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Saving...' : 'Register Patient'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Patient Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Patient Details"
        subtitle={`Update attributes for ${selectedPatient?.patientId}`}
      >
        <form onSubmit={handleUpdate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
            <FormField
              label="Date of Birth"
              name="dob"
              type="date"
              value={formData.dob}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Gender"
              name="gender"
              type="select"
              value={formData.gender}
              onChange={handleInputChange}
              options={[
                { value: 'M', label: 'Male' },
                { value: 'F', label: 'Female' },
                { value: 'Other', label: 'Other' }
              ]}
              required
            />
            <FormField
              label="Phone Number"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              required
            />
          </div>

          <FormField
            label="Address"
            name="address"
            value={formData.address}
            onChange={handleInputChange}
          />

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsEditModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Updating...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Cascading Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteId}
        title="Delete Patient & Complete Medical Subgraph"
        message={`Are you sure you want to delete patient ${deleteId}? This will remove all their appointments, consultations, treatments, prescriptions, lab tests, bills, and insurance claims. Doctor, Department, and shared catalog nodes will NOT be touched.`}
        confirmText="Confirm Delete"
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
        isLoading={isSubmitting}
        isDestructive={true}
      />
    </div>
  );
}
