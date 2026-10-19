import React, { useState, useEffect } from 'react';
import {
  DollarSign, FileText, Plus, ShieldCheck, CheckCircle2, Clock, Trash2, Edit2, Download
} from 'lucide-react';
import {
  getBills, createBill, updateBill, deleteBill, updateClaim,
  getPatientBillingReport, getInsuranceCompanies, getConsultations
} from '../api';
import Table from '../components/Table';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import FormField from '../components/FormField';
import ErrorBanner from '../components/ErrorBanner';

export default function Billing() {
  const [activeTab, setActiveTab] = useState('bills'); // 'bills' | 'claims' | 'report'
  const [bills, setBills] = useState([]);
  const [reportRows, setReportRows] = useState([]);
  const [consultations, setConsultations] = useState([]);
  const [insuranceCompanies, setInsuranceCompanies] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchPatient, setSearchPatient] = useState('');
  const [modeFilter, setModeFilter] = useState('');

  // Modals
  const [isCreateBillModalOpen, setIsCreateBillModalOpen] = useState(false);
  const [isUpdateClaimModalOpen, setIsUpdateClaimModalOpen] = useState(false);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [deleteBillId, setDeleteBillId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form states
  const [billForm, setBillForm] = useState({
    consultationId: '',
    consultationCharge: 500,
    labCharge: 350,
    pharmacyCharge: 150,
    roomCharge: 0,
    otherCharge: 50,
    paymentMode: 'Direct',
    paymentStatus: 'Paid',
    withClaim: false,
    claimCompanyId: 'WellnessCorp',
    claimAmount: 1050
  });

  const [claimUpdateForm, setClaimUpdateForm] = useState({
    status: 'Approved',
    approvedAmount: 0
  });

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [bRes, rRes, cRes, icRes] = await Promise.all([
        getBills({ patient: searchPatient || undefined, paymentMode: modeFilter || undefined }),
        getPatientBillingReport(),
        getConsultations(),
        getInsuranceCompanies()
      ]);
      setBills(bRes.data || []);
      setReportRows(rRes.data || []);
      setConsultations(cRes.data || []);
      setInsuranceCompanies(icRes.data || []);

      if (cRes.data?.length > 0 && !billForm.consultationId) {
        setBillForm((prev) => ({ ...prev, consultationId: cRes.data[0].consultId }));
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch billing data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [searchPatient, modeFilter]);

  // Recalculate auto total
  const calculatedTotal =
    Number(billForm.consultationCharge || 0) +
    Number(billForm.labCharge || 0) +
    Number(billForm.pharmacyCharge || 0) +
    Number(billForm.roomCharge || 0) +
    Number(billForm.otherCharge || 0);

  const handleCreateBill = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const payload = {
        consultationId: billForm.consultationId,
        consultationCharge: parseFloat(billForm.consultationCharge) || 0,
        labCharge: parseFloat(billForm.labCharge) || 0,
        pharmacyCharge: parseFloat(billForm.pharmacyCharge) || 0,
        roomCharge: parseFloat(billForm.roomCharge) || 0,
        otherCharge: parseFloat(billForm.otherCharge) || 0,
        paymentMode: billForm.paymentMode,
        paymentStatus: billForm.paymentStatus,
        claim:
          billForm.paymentMode === 'Insurance'
            ? {
                companyId: billForm.claimCompanyId,
                claimAmount: parseFloat(billForm.claimAmount) || calculatedTotal
              }
            : null
      };

      await createBill(payload);
      setIsCreateBillModalOpen(false);
      fetchData();
    } catch (err) {
      alert(`Error creating bill: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenClaimUpdate = (bill) => {
    setSelectedClaim({
      claimId: bill.claimId,
      billNo: bill.billNo,
      patientName: bill.patientName,
      claimAmount: bill.claimAmount
    });
    setClaimUpdateForm({
      status: bill.claimStatus || 'Approved',
      approvedAmount: bill.approvedAmount || bill.claimAmount || 0
    });
    setIsUpdateClaimModalOpen(true);
  };

  const handleUpdateClaim = async (e) => {
    e.preventDefault();
    if (!selectedClaim) return;
    setIsSubmitting(true);
    try {
      await updateClaim(selectedClaim.claimId, {
        status: claimUpdateForm.status,
        approvedAmount: parseFloat(claimUpdateForm.approvedAmount) || 0
      });
      setIsUpdateClaimModalOpen(false);
      fetchData();
    } catch (err) {
      alert(`Error updating claim: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteBill = async () => {
    if (!deleteBillId) return;
    setIsSubmitting(true);
    try {
      await deleteBill(deleteBillId);
      setDeleteBillId(null);
      fetchData();
    } catch (err) {
      alert(`Error deleting bill: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const billColumns = [
    {
      header: 'Bill No',
      accessor: 'billNo',
      render: (r) => (
        <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
          {r.billNo}
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
      header: 'Total Amount',
      accessor: 'totalAmount',
      render: (r) => (
        <span className="font-bold text-slate-900 text-sm">
          ${Number(r.totalAmount || 0).toLocaleString()}
        </span>
      )
    },
    {
      header: 'Payment Mode',
      accessor: 'paymentMode',
      render: (r) => (
        <span
          className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
            r.paymentMode === 'Insurance'
              ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
          }`}
        >
          {r.paymentMode === 'Insurance' ? <ShieldCheck className="w-3 h-3 text-indigo-600" /> : <DollarSign className="w-3 h-3 text-emerald-600" />}
          <span>{r.paymentMode}</span>
        </span>
      )
    },
    {
      header: 'Status',
      accessor: 'paymentStatus',
      render: (r) => (
        <span
          className={`inline-flex px-2 py-0.5 rounded-md text-[11px] font-bold ${
            r.paymentStatus === 'Paid'
              ? 'bg-emerald-100 text-emerald-800'
              : 'bg-amber-100 text-amber-800'
          }`}
        >
          {r.paymentStatus || 'Pending'}
        </span>
      )
    },
    {
      header: 'Insurance Claim',
      accessor: 'claimId',
      render: (r) =>
        r.claimId ? (
          <div>
            <div className="flex items-center space-x-1 text-xs font-semibold text-indigo-900">
              <span>${Number(r.claimAmount || 0).toFixed(0)}</span>
              <span className="text-[10px] text-slate-400">({r.claimStatus || 'Pending'})</span>
            </div>
            <button
              onClick={() => handleOpenClaimUpdate(r)}
              className="text-[11px] text-indigo-600 hover:text-indigo-800 font-semibold underline mt-0.5 block"
            >
              Update Claim
            </button>
          </div>
        ) : (
          <span className="text-xs text-slate-400">None</span>
        )
    },
    {
      header: 'Date',
      accessor: 'billDate',
      render: (r) => <span className="text-xs text-slate-500">{String(r.billDate).substring(0, 10)}</span>
    },
    {
      header: 'Actions',
      align: 'right',
      render: (r) => (
        <button
          onClick={() => setDeleteBillId(r.billNo)}
          title="Delete Bill & Claim"
          className="p-1.5 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors ml-auto block"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      )
    }
  ];

  const reportColumns = [
    {
      header: 'Patient Name',
      accessor: 'patient',
      render: (r) => <span className="font-semibold text-slate-900">{r.patient}</span>
    },
    {
      header: 'Total Bill ($)',
      accessor: 'totalBill',
      align: 'right',
      render: (r) => <span className="font-bold text-slate-900">${Number(r.totalBill || 0).toLocaleString()}</span>
    },
    {
      header: 'Claim Amount ($)',
      accessor: 'claimAmount',
      align: 'right',
      render: (r) => <span className="text-slate-600">${Number(r.claimAmount || 0).toLocaleString()}</span>
    },
    {
      header: 'Approved Amount ($)',
      accessor: 'approvedAmount',
      align: 'right',
      render: (r) => (
        <span className="font-medium text-emerald-700">
          ${Number(r.approvedAmount || 0).toLocaleString()}
        </span>
      )
    },
    {
      header: 'Patient Payable Net ($)',
      accessor: 'patientPayable',
      align: 'right',
      render: (r) => (
        <span className="font-bold text-sky-800 text-sm">
          ${Number(r.patientPayable || 0).toLocaleString()}
        </span>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Hospital Billing & Claims
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Generate itemized invoices, manage insurance claims, and audit patient balances.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center bg-slate-200/70 p-1 rounded-xl w-max">
          <button
            onClick={() => setActiveTab('bills')}
            className={`flex items-center space-x-1.5 px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'bills' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <DollarSign className="w-3.5 h-3.5 text-amber-600" />
            <span>Invoices ({bills.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('report')}
            className={`flex items-center space-x-1.5 px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'report' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-indigo-600" />
            <span>Billing Report ({reportRows.length})</span>
          </button>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={fetchData} />

      {activeTab === 'bills' ? (
        <div className="space-y-4">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs flex flex-wrap items-center gap-3">
            <div className="w-full sm:w-44">
              <select
                value={modeFilter}
                onChange={(e) => setModeFilter(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-medium"
              >
                <option value="">All Payment Modes</option>
                <option value="Direct">Direct</option>
                <option value="Insurance">Insurance</option>
              </select>
            </div>
          </div>

          <Table
            columns={billColumns}
            data={bills}
            searchValue={searchPatient}
            onSearchChange={setSearchPatient}
            searchPlaceholder="Search bills by patient name..."
            isLoading={isLoading}
            emptyMessage="No billing records found."
            actionButton={
              <button
                onClick={() => setIsCreateBillModalOpen(true)}
                className="flex items-center space-x-1.5 px-4 py-2 text-sm font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-xl shadow-xs transition-colors shrink-0"
              >
                <Plus className="w-4 h-4" />
                <span>Create Bill</span>
              </button>
            }
          />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-sky-50 border border-sky-200 p-4 rounded-xl text-xs text-sky-900 flex items-center justify-between">
            <div>
              <strong className="block text-sm font-bold text-sky-950">Hospital-Wide Billing Report</strong>
              <p className="mt-0.5">Aggregates Total Bill, Insurance Claims, and Net Patient Payable across all patients.</p>
            </div>
          </div>
          <Table
            columns={reportColumns}
            data={reportRows}
            isLoading={isLoading}
            emptyMessage="No report rows available."
          />
        </div>
      )}

      {/* Create Bill Modal */}
      <Modal
        isOpen={isCreateBillModalOpen}
        onClose={() => setIsCreateBillModalOpen(false)}
        title="Generate Invoice / Bill"
        subtitle="Calculates total amount on the server and attaches optional insurance claims in Neo4j."
      >
        <form onSubmit={handleCreateBill} className="space-y-4">
          <FormField
            label="Associated Consultation"
            name="consultationId"
            type="select"
            value={billForm.consultationId}
            onChange={(e) => setBillForm({ ...billForm, consultationId: e.target.value })}
            options={consultations.map((c) => ({
              value: c.consultId,
              label: `${c.consultId} - ${c.patientName} (${c.diagnosis || 'Checkup'})`
            }))}
            required
          />

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
            <FormField
              label="Consultation Fee"
              name="consultationCharge"
              type="number"
              min="0"
              value={billForm.consultationCharge}
              onChange={(e) => setBillForm({ ...billForm, consultationCharge: e.target.value })}
            />
            <FormField
              label="Lab Diagnostics"
              name="labCharge"
              type="number"
              min="0"
              value={billForm.labCharge}
              onChange={(e) => setBillForm({ ...billForm, labCharge: e.target.value })}
            />
            <FormField
              label="Pharmacy Charge"
              name="pharmacyCharge"
              type="number"
              min="0"
              value={billForm.pharmacyCharge}
              onChange={(e) => setBillForm({ ...billForm, pharmacyCharge: e.target.value })}
            />
            <FormField
              label="Room / Ward"
              name="roomCharge"
              type="number"
              min="0"
              value={billForm.roomCharge}
              onChange={(e) => setBillForm({ ...billForm, roomCharge: e.target.value })}
            />
            <FormField
              label="Other Hospital Fees"
              name="otherCharge"
              type="number"
              min="0"
              value={billForm.otherCharge}
              onChange={(e) => setBillForm({ ...billForm, otherCharge: e.target.value })}
            />
            <div className="flex flex-col justify-end p-2 bg-white rounded-lg border border-slate-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Calculated Total</span>
              <span className="text-lg font-extrabold text-slate-900">${calculatedTotal.toLocaleString()}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Payment Mode"
              name="paymentMode"
              type="select"
              value={billForm.paymentMode}
              onChange={(e) => setBillForm({ ...billForm, paymentMode: e.target.value })}
              options={[
                { value: 'Direct', label: 'Direct Payment' },
                { value: 'Insurance', label: 'Insurance Claim' }
              ]}
              required
            />
            <FormField
              label="Payment Status"
              name="paymentStatus"
              type="select"
              value={billForm.paymentStatus}
              onChange={(e) => setBillForm({ ...billForm, paymentStatus: e.target.value })}
              options={[
                { value: 'Paid', label: 'Paid in Full' },
                { value: 'Pending', label: 'Payment Pending' }
              ]}
              required
            />
          </div>

          {billForm.paymentMode === 'Insurance' && (
            <div className="p-4 bg-indigo-50/50 rounded-xl border border-indigo-100 space-y-3">
              <span className="text-xs font-bold text-indigo-900 uppercase tracking-wider block">
                Insurance Claim Parameters
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <FormField
                  label="Insurance Company"
                  name="claimCompanyId"
                  type="select"
                  value={billForm.claimCompanyId}
                  onChange={(e) => setBillForm({ ...billForm, claimCompanyId: e.target.value })}
                  options={insuranceCompanies.map((c) => ({
                    value: c.name,
                    label: c.name
                  }))}
                />
                <FormField
                  label="Claimed Amount ($)"
                  name="claimAmount"
                  type="number"
                  min="0"
                  value={billForm.claimAmount}
                  onChange={(e) => setBillForm({ ...billForm, claimAmount: e.target.value })}
                />
              </div>
            </div>
          )}

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsCreateBillModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Creating...' : 'Generate Bill'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Claim Status Update Modal */}
      <Modal
        isOpen={isUpdateClaimModalOpen}
        onClose={() => setIsUpdateClaimModalOpen(false)}
        title="Update Insurance Claim"
        subtitle={`Adjust approval decision and approved amount for ${selectedClaim?.claimId}`}
      >
        <form onSubmit={handleUpdateClaim} className="space-y-4">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 flex justify-between items-center">
            <span>Claim for: <strong className="text-slate-900">{selectedClaim?.patientName}</strong></span>
            <span>Original Claim: <strong className="text-slate-900">${Number(selectedClaim?.claimAmount || 0).toLocaleString()}</strong></span>
          </div>

          <FormField
            label="Claim Status"
            name="status"
            type="select"
            value={claimUpdateForm.status}
            onChange={(e) => setClaimUpdateForm({ ...claimUpdateForm, status: e.target.value })}
            options={[
              { value: 'Approved', label: 'Approved' },
              { value: 'Rejected', label: 'Rejected' },
              { value: 'Pending', label: 'Pending / In Review' },
              { value: 'Submitted', label: 'Submitted' }
            ]}
            required
          />

          <FormField
            label="Approved Amount ($)"
            name="approvedAmount"
            type="number"
            min="0"
            step="10"
            value={claimUpdateForm.approvedAmount}
            onChange={(e) => setClaimUpdateForm({ ...claimUpdateForm, approvedAmount: e.target.value })}
            required
            helperText="The approved amount offsets the total bill to calculate net patient payable."
          />

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsUpdateClaimModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Saving...' : 'Update Claim Status'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteBillId}
        title="Delete Bill"
        message={`Are you sure you want to delete bill ${deleteBillId}? This will remove the bill and its associated insurance claim node.`}
        confirmText="Confirm Delete"
        onConfirm={handleDeleteBill}
        onCancel={() => setDeleteBillId(null)}
        isLoading={isSubmitting}
        isDestructive={true}
      />
    </div>
  );
}
