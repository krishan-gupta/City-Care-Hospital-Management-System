import React, { useState, useEffect } from 'react';
import { Plus, Calendar, Clock, Edit3, Trash2, CheckCircle, XCircle } from 'lucide-react';
import {
  getAppointments, createAppointment, updateAppointment, deleteAppointment,
  getDoctors, getPatients, getDepartments
} from '../api';
import Table from '../components/Table';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import FormField from '../components/FormField';
import ErrorBanner from '../components/ErrorBanner';

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [doctorFilter, setDoctorFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  // Modals
  const [isBookModalOpen, setIsBookModalOpen] = useState(false);
  const [isRescheduleModalOpen, setIsRescheduleModalOpen] = useState(false);
  const [selectedAppt, setSelectedAppt] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Forms
  const [bookData, setBookData] = useState({
    patientId: '',
    doctorId: '',
    date: new Date().toISOString().substring(0, 10),
    time: '10:00'
  });

  const [rescheduleData, setRescheduleData] = useState({
    date: '',
    time: '',
    status: 'Scheduled'
  });

  const fetchAppointments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getAppointments({
        status: statusFilter || undefined,
        doctor: doctorFilter || undefined,
        department: deptFilter || undefined
      });
      setAppointments(res.data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch appointments.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load lookup data
    Promise.all([
      getDoctors(),
      getPatients({ page: 1, size: 50 }),
      getDepartments()
    ]).then(([dRes, pRes, depRes]) => {
      setDoctors(dRes.data || []);
      setPatients(pRes.data.items || []);
      setDepartments(depRes.data || []);
      if (pRes.data.items?.length > 0) {
        setBookData((prev) => ({ ...prev, patientId: pRes.data.items[0].patientId }));
      }
      if (dRes.data?.length > 0) {
        setBookData((prev) => ({ ...prev, doctorId: dRes.data[0].empId }));
      }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    fetchAppointments();
  }, [statusFilter, doctorFilter, deptFilter]);

  const handleBook = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createAppointment(bookData);
      setIsBookModalOpen(false);
      fetchAppointments();
    } catch (err) {
      alert(`Error booking appointment: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenReschedule = (appt) => {
    setSelectedAppt(appt);
    setRescheduleData({
      date: appt.date ? String(appt.date).substring(0, 10) : '',
      time: appt.time ? String(appt.time).substring(0, 5) : '10:00',
      status: appt.status || 'Scheduled'
    });
    setIsRescheduleModalOpen(true);
  };

  const handleReschedule = async (e) => {
    e.preventDefault();
    if (!selectedAppt) return;
    setIsSubmitting(true);
    try {
      await updateAppointment(selectedAppt.apptId, rescheduleData);
      setIsRescheduleModalOpen(false);
      fetchAppointments();
    } catch (err) {
      alert(`Error updating appointment: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setIsSubmitting(true);
    try {
      await deleteAppointment(deleteId);
      setDeleteId(null);
      fetchAppointments();
    } catch (err) {
      alert(`Error deleting appointment: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'Scheduled':
        return 'bg-sky-50 text-sky-700 border-sky-200';
      case 'Cancelled':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'No-show':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const columns = [
    {
      header: 'Appt ID',
      accessor: 'apptId',
      render: (r) => (
        <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
          {r.apptId}
        </span>
      )
    },
    {
      header: 'Patient',
      accessor: 'patientName',
      render: (r) => (
        <div>
          <span className="font-semibold text-slate-900 block">{r.patientName}</span>
          <span className="text-xs text-slate-400 font-mono">{r.patientId}</span>
        </div>
      )
    },
    {
      header: 'Doctor & Department',
      accessor: 'doctorName',
      render: (r) => (
        <div>
          <span className="font-semibold text-slate-900 block">Dr. {r.doctorName}</span>
          <span className="text-xs text-slate-500">{r.departmentName || r.doctorSpecialization || 'Clinical'}</span>
        </div>
      )
    },
    {
      header: 'Date & Time',
      accessor: 'date',
      render: (r) => (
        <div className="text-xs">
          <div className="flex items-center space-x-1.5 font-medium text-slate-800">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{r.date ? String(r.date).substring(0, 10) : '—'}</span>
          </div>
          {r.time && (
            <div className="flex items-center space-x-1.5 text-slate-400 mt-0.5">
              <Clock className="w-3.5 h-3.5" />
              <span>{String(r.time).substring(0, 5)}</span>
            </div>
          )}
        </div>
      )
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (r) => (
        <span className={`inline-flex px-2.5 py-1 text-xs font-semibold rounded-full border ${getStatusBadge(r.status)}`}>
          {r.status || 'Scheduled'}
        </span>
      )
    },
    {
      header: 'Actions',
      align: 'right',
      render: (r) => (
        <div className="flex items-center justify-end space-x-1.5">
          <button
            onClick={() => handleOpenReschedule(r)}
            title="Reschedule or update status"
            className="p-1.5 text-sky-600 hover:text-sky-800 hover:bg-sky-50 rounded-lg transition-colors flex items-center space-x-1 text-xs font-semibold"
          >
            <Edit3 className="w-4 h-4" />
            <span className="hidden sm:inline">Modify</span>
          </button>
          <button
            onClick={() => setDeleteId(r.apptId)}
            title="Delete Appointment & Consult Subgraph"
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
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Appointments Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            Schedule visits, track status, and coordinate patient-doctor encounters.
          </p>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={fetchAppointments} />

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-2xs flex flex-wrap items-center gap-3">
        <div className="w-full sm:w-44">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <option value="">All Statuses</option>
            <option value="Scheduled">Scheduled</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
            <option value="No-show">No-show</option>
          </select>
        </div>

        <div className="w-full sm:w-48">
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.deptId || d.name} value={d.name}>{d.name}</option>
            ))}
          </select>
        </div>

        <div className="w-full sm:w-48">
          <select
            value={doctorFilter}
            onChange={(e) => setDoctorFilter(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <option value="">All Doctors</option>
            {doctors.map((doc) => (
              <option key={doc.empId} value={doc.empId}>Dr. {doc.name}</option>
            ))}
          </select>
        </div>

        {(statusFilter || deptFilter || doctorFilter) && (
          <button
            onClick={() => { setStatusFilter(''); setDeptFilter(''); setDoctorFilter(''); }}
            className="text-xs font-semibold text-rose-600 hover:text-rose-800 ml-auto"
          >
            Reset Filters
          </button>
        )}
      </div>

      <Table
        columns={columns}
        data={appointments}
        isLoading={isLoading}
        emptyMessage="No appointments match the criteria."
        actionButton={
          <button
            onClick={() => setIsBookModalOpen(true)}
            className="flex items-center space-x-1.5 px-4 py-2 text-sm font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs transition-colors shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Book Appointment</span>
          </button>
        }
      />

      {/* Book Appointment Modal */}
      <Modal
        isOpen={isBookModalOpen}
        onClose={() => setIsBookModalOpen(false)}
        title="Schedule New Appointment"
        subtitle="Links :Patient and :Doctor to a newly generated :Appointments node in Neo4j."
      >
        <form onSubmit={handleBook} className="space-y-4">
          <FormField
            label="Select Patient"
            name="patientId"
            type="select"
            value={bookData.patientId}
            onChange={(e) => setBookData({ ...bookData, patientId: e.target.value })}
            options={patients.map((p) => ({
              value: p.patientId,
              label: `${p.patientId} - ${p.name}`
            }))}
            required
          />

          <FormField
            label="Select Doctor"
            name="doctorId"
            type="select"
            value={bookData.doctorId}
            onChange={(e) => setBookData({ ...bookData, doctorId: e.target.value })}
            options={doctors.map((d) => ({
              value: d.empId,
              label: `Dr. ${d.name} (${d.specialization || d.department || 'General'})`
            }))}
            required
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Date"
              name="date"
              type="date"
              value={bookData.date}
              onChange={(e) => setBookData({ ...bookData, date: e.target.value })}
              required
            />
            <FormField
              label="Time"
              name="time"
              type="time"
              value={bookData.time}
              onChange={(e) => setBookData({ ...bookData, time: e.target.value })}
              required
            />
          </div>

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsBookModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Booking...' : 'Book Appointment'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Modify / Reschedule Modal */}
      <Modal
        isOpen={isRescheduleModalOpen}
        onClose={() => setIsRescheduleModalOpen(false)}
        title="Modify Appointment"
        subtitle={`Update date, time, or status for ${selectedAppt?.apptId}`}
      >
        <form onSubmit={handleReschedule} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Date"
              name="date"
              type="date"
              value={rescheduleData.date}
              onChange={(e) => setRescheduleData({ ...rescheduleData, date: e.target.value })}
              required
            />
            <FormField
              label="Time"
              name="time"
              type="time"
              value={rescheduleData.time}
              onChange={(e) => setRescheduleData({ ...rescheduleData, time: e.target.value })}
              required
            />
          </div>

          <FormField
            label="Appointment Status"
            name="status"
            type="select"
            value={rescheduleData.status}
            onChange={(e) => setRescheduleData({ ...rescheduleData, status: e.target.value })}
            options={[
              { value: 'Scheduled', label: 'Scheduled' },
              { value: 'Completed', label: 'Completed' },
              { value: 'Cancelled', label: 'Cancelled' },
              { value: 'No-show', label: 'No-show' }
            ]}
            required
          />

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsRescheduleModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Saving...' : 'Save Updates'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Cascading Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteId}
        title="Delete Appointment"
        message={`Are you sure you want to delete appointment ${deleteId}? This will remove this appointment and its associated consultation subgraph (prescriptions, lab tests, bills). Patient and Doctor records remain intact.`}
        confirmText="Delete Appointment"
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
        isLoading={isSubmitting}
        isDestructive={true}
      />
    </div>
  );
}
