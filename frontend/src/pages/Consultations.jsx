import React, { useState, useEffect } from 'react';
import {
  Stethoscope, FlaskConical, Plus, Trash, CheckCircle2, AlertTriangle, Clock, FileEdit
} from 'lucide-react';
import {
  getConsultations, createConsultation, getLabTests, updateLabTest,
  getAppointments, getMedicines, getTechnicians
} from '../api';
import Table from '../components/Table';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import ErrorBanner from '../components/ErrorBanner';

export default function Consultations() {
  const [activeTab, setActiveTab] = useState('consultations'); // 'consultations' | 'labtests'
  const [consultations, setConsultations] = useState([]);
  const [labTests, setLabTests] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [availableMedicines, setAvailableMedicines] = useState([]);
  const [availableTechnicians, setAvailableTechnicians] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter
  const [labFilter, setLabFilter] = useState('');

  // New Consultation Modal
  const [isConsultModalOpen, setIsConsultModalOpen] = useState(false);
  const [consultForm, setConsultForm] = useState({
    appointmentId: '',
    diagnosis: '',
    notes: '',
    medicines: [],
    labTests: []
  });

  // Lab Test Update Modal
  const [isLabModalOpen, setIsLabModalOpen] = useState(false);
  const [selectedLabTest, setSelectedLabTest] = useState(null);
  const [labResultData, setLabResultData] = useState({
    result: '',
    resultStatus: 'Normal'
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [cRes, lRes, aRes, mRes, tRes] = await Promise.all([
        getConsultations(),
        getLabTests({ status: labFilter || undefined }),
        getAppointments({ status: 'Scheduled' }),
        getMedicines(),
        getTechnicians()
      ]);
      setConsultations(cRes.data || []);
      setLabTests(lRes.data || []);
      setAppointments(aRes.data || []);
      setAvailableMedicines(mRes.data || []);
      setAvailableTechnicians(tRes.data || []);

      if (aRes.data?.length > 0 && !consultForm.appointmentId) {
        setConsultForm((prev) => ({ ...prev, appointmentId: aRes.data[0].apptId }));
      }
    } catch (err) {
      setError(err.message || 'Failed to load consultation or lab records.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [labFilter]);

  // Form helpers for medicines and lab tests inside consultation
  const addMedicineRow = () => {
    setConsultForm((prev) => ({
      ...prev,
      medicines: [
        ...prev.medicines,
        {
          medId: availableMedicines[0]?.name || 'Amoxicillin 500mg',
          dosage: '1 tablet twice daily',
          durationDays: 7
        }
      ]
    }));
  };

  const removeMedicineRow = (idx) => {
    setConsultForm((prev) => ({
      ...prev,
      medicines: prev.medicines.filter((_, i) => i !== idx)
    }));
  };

  const addLabTestRow = () => {
    setConsultForm((prev) => ({
      ...prev,
      labTests: [
        ...prev.labTests,
        {
          testType: 'Complete Blood Count (CBC)',
          charge: 450.0,
          technicianId: availableTechnicians[0]?.empId || ''
        }
      ]
    }));
  };

  const removeLabTestRow = (idx) => {
    setConsultForm((prev) => ({
      ...prev,
      labTests: prev.labTests.filter((_, i) => i !== idx)
    }));
  };

  const handleCreateConsultation = async (e) => {
    e.preventDefault();
    if (!consultForm.appointmentId) {
      alert('Please select an appointment.');
      return;
    }
    setIsSubmitting(true);
    try {
      await createConsultation(consultForm);
      setIsConsultModalOpen(false);
      setConsultForm({
        appointmentId: appointments[0]?.apptId || '',
        diagnosis: '',
        notes: '',
        medicines: [],
        labTests: []
      });
      fetchData();
    } catch (err) {
      alert(`Error creating consultation: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenLabUpdate = (test) => {
    setSelectedLabTest(test);
    setLabResultData({
      result: test.result || '',
      resultStatus: test.resultStatus === 'Abnormal' ? 'Abnormal' : 'Normal'
    });
    setIsLabModalOpen(true);
  };

  const handleUpdateLabResult = async (e) => {
    e.preventDefault();
    if (!selectedLabTest) return;
    setIsSubmitting(true);
    try {
      await updateLabTest(selectedLabTest.testId, labResultData);
      setIsLabModalOpen(false);
      fetchData();
    } catch (err) {
      alert(`Error updating lab test: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const consultColumns = [
    {
      header: 'Consult ID',
      accessor: 'consultId',
      render: (r) => (
        <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
          {r.consultId}
        </span>
      )
    },
    {
      header: 'Patient & Doctor',
      accessor: 'patientName',
      render: (r) => (
        <div>
          <span className="font-semibold text-slate-900 block">{r.patientName}</span>
          <span className="text-xs text-slate-500">Dr. {r.doctorName}</span>
        </div>
      )
    },
    {
      header: 'Diagnosis / Reason',
      accessor: 'diagnosis',
      render: (r) => (
        <span className="font-medium text-slate-800">{r.diagnosis}</span>
      )
    },
    {
      header: 'Prescriptions Issued',
      accessor: 'prescriptions',
      render: (r) => (
        <div className="flex flex-wrap gap-1 max-w-xs">
          {r.prescriptions && r.prescriptions.length > 0 && r.prescriptions[0].rxId ? (
            r.prescriptions.map((rx, idx) => (
              <span key={idx} className="bg-orange-50 text-orange-700 border border-orange-200 px-2 py-0.5 rounded text-[11px] font-medium">
                {rx.treatmentType || 'Rx item'}
              </span>
            ))
          ) : (
            <span className="text-xs text-slate-400">None</span>
          )}
        </div>
      )
    },
    {
      header: 'Ordered Tests',
      accessor: 'labTests',
      render: (r) => (
        <div className="flex flex-wrap gap-1 max-w-xs">
          {r.labTests && r.labTests.length > 0 && r.labTests[0].testId ? (
            r.labTests.map((lt, idx) => (
              <span key={idx} className="bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded text-[11px] font-medium">
                {lt.testType || 'Diagnostic'}
              </span>
            ))
          ) : (
            <span className="text-xs text-slate-400">None</span>
          )}
        </div>
      )
    },
    {
      header: 'Date',
      accessor: 'date',
      render: (r) => <span className="text-xs text-slate-500">{String(r.date).substring(0, 10)}</span>
    }
  ];

  const labColumns = [
    {
      header: 'Test ID',
      accessor: 'testId',
      render: (r) => (
        <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
          {r.testId}
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
      header: 'Test Name / Type',
      accessor: 'testType',
      render: (r) => (
        <span className="font-medium text-slate-800">{r.testType}</span>
      )
    },
    {
      header: 'Status & Result',
      accessor: 'resultStatus',
      render: (r) => {
        const isAbnormal = r.resultStatus === 'Abnormal';
        const isNormal = r.resultStatus === 'Normal';
        return (
          <div>
            <span
              className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                isAbnormal
                  ? 'bg-rose-100 text-rose-800 border-rose-300'
                  : isNormal
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
            >
              {isAbnormal ? <AlertTriangle className="w-3 h-3 text-rose-600" /> : isNormal ? <CheckCircle2 className="w-3 h-3 text-emerald-600" /> : <Clock className="w-3 h-3" />}
              <span>{r.resultStatus || 'Pending'}</span>
            </span>
            {r.result && (
              <p className={`text-xs mt-1 font-medium ${isAbnormal ? 'text-rose-700 font-bold' : 'text-slate-600'}`}>
                {r.result}
              </p>
            )}
          </div>
        );
      }
    },
    {
      header: 'Charge',
      accessor: 'charge',
      render: (r) => <span className="font-medium text-slate-800">${r.charge ? Number(r.charge).toFixed(2) : '0.00'}</span>
    },
    {
      header: 'Actions',
      align: 'right',
      render: (r) => (
        <button
          onClick={() => handleOpenLabUpdate(r)}
          className="px-3 py-1.5 text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-lg transition-colors flex items-center space-x-1 ml-auto"
        >
          <FileEdit className="w-3.5 h-3.5" />
          <span>Enter Result</span>
        </button>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Consultations & Laboratory
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Conduct transactional consultations, prescribe treatments, and log lab diagnostics.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center bg-slate-200/70 p-1 rounded-xl w-max">
          <button
            onClick={() => setActiveTab('consultations')}
            className={`flex items-center space-x-1.5 px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'consultations' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Stethoscope className="w-3.5 h-3.5 text-teal-600" />
            <span>Consultations ({consultations.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('labtests')}
            className={`flex items-center space-x-1.5 px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'labtests' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5 text-rose-600" />
            <span>Lab Tests ({labTests.length})</span>
          </button>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={fetchData} />

      {activeTab === 'consultations' ? (
        <Table
          columns={consultColumns}
          data={consultations}
          isLoading={isLoading}
          emptyMessage="No consultations registered."
          actionButton={
            <button
              onClick={() => setIsConsultModalOpen(true)}
              className="flex items-center space-x-1.5 px-4 py-2 text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-xl shadow-xs transition-colors shrink-0"
            >
              <Plus className="w-4 h-4" />
              <span>New Consultation</span>
            </button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-slate-500 uppercase">Filter Status:</span>
              <select
                value={labFilter}
                onChange={(e) => setLabFilter(e.target.value)}
                className="px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg text-slate-800 font-medium"
              >
                <option value="">All Tests</option>
                <option value="Normal">Normal</option>
                <option value="Abnormal">Abnormal</option>
                <option value="Pending">Pending / Needs Details</option>
              </select>
            </div>
          </div>
          <Table
            columns={labColumns}
            data={labTests}
            isLoading={isLoading}
            emptyMessage="No lab tests found."
          />
        </div>
      )}

      {/* Transactional Consultation Creation Modal */}
      <Modal
        isOpen={isConsultModalOpen}
        onClose={() => setIsConsultModalOpen(false)}
        title="Record Clinical Consultation"
        subtitle="Saves consultation, prescription, and lab tests atomically in a single Neo4j transaction."
        maxWidth="max-w-3xl"
      >
        <form onSubmit={handleCreateConsultation} className="space-y-5">
          <FormField
            label="Select Scheduled Appointment"
            name="appointmentId"
            type="select"
            value={consultForm.appointmentId}
            onChange={(e) => setConsultForm({ ...consultForm, appointmentId: e.target.value })}
            options={appointments.map((a) => ({
              value: a.apptId,
              label: `${a.apptId} - ${a.patientName} with Dr. ${a.doctorName} (${String(a.date).substring(0, 10)})`
            }))}
            required
            helperText="The appointment status will automatically be updated to 'Completed'"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Diagnosis"
              name="diagnosis"
              value={consultForm.diagnosis}
              onChange={(e) => setConsultForm({ ...consultForm, diagnosis: e.target.value })}
              placeholder="e.g. Hypertension, Acute Bronchitis, Migraine"
              required
            />
            <FormField
              label="Clinical Notes / Recommendations"
              name="notes"
              value={consultForm.notes}
              onChange={(e) => setConsultForm({ ...consultForm, notes: e.target.value })}
              placeholder="e.g. Dietary review, re-check in 2 weeks"
            />
          </div>

          {/* Medicines Sub-section */}
          <div className="p-4 bg-orange-50/40 rounded-xl border border-orange-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-orange-900 uppercase tracking-wider flex items-center space-x-1.5">
                <span>Prescribe Medicines</span>
              </span>
              <button
                type="button"
                onClick={addMedicineRow}
                className="text-xs font-semibold text-orange-700 hover:text-orange-900 flex items-center space-x-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Medicine</span>
              </button>
            </div>

            {consultForm.medicines.map((m, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-2 items-center bg-white p-2.5 rounded-lg border border-orange-100">
                <div className="col-span-5">
                  <select
                    value={m.medId}
                    onChange={(e) => {
                      const updated = [...consultForm.medicines];
                      updated[idx].medId = e.target.value;
                      setConsultForm({ ...consultForm, medicines: updated });
                    }}
                    className="w-full text-xs p-1.5 bg-slate-50 border border-slate-200 rounded-lg"
                  >
                    {availableMedicines.map((item) => (
                      <option key={item.medId} value={item.name}>{item.name}</option>
                    ))}
                  </select>
                </div>
                <div className="col-span-4">
                  <input
                    type="text"
                    value={m.dosage}
                    onChange={(e) => {
                      const updated = [...consultForm.medicines];
                      updated[idx].dosage = e.target.value;
                      setConsultForm({ ...consultForm, medicines: updated });
                    }}
                    placeholder="Dosage instruction"
                    className="w-full text-xs p-1.5 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <input
                    type="number"
                    min="1"
                    value={m.durationDays}
                    onChange={(e) => {
                      const updated = [...consultForm.medicines];
                      updated[idx].durationDays = parseInt(e.target.value) || 1;
                      setConsultForm({ ...consultForm, medicines: updated });
                    }}
                    placeholder="Days"
                    className="w-full text-xs p-1.5 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
                <div className="col-span-1 text-center">
                  <button
                    type="button"
                    onClick={() => removeMedicineRow(idx)}
                    className="text-rose-500 hover:text-rose-700 p-1"
                  >
                    <Trash className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Lab Tests Sub-section */}
          <div className="p-4 bg-rose-50/40 rounded-xl border border-rose-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-rose-900 uppercase tracking-wider flex items-center space-x-1.5">
                <span>Order Lab Tests</span>
              </span>
              <button
                type="button"
                onClick={addLabTestRow}
                className="text-xs font-semibold text-rose-700 hover:text-rose-900 flex items-center space-x-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Lab Test</span>
              </button>
            </div>

            {consultForm.labTests.map((lt, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-2 items-center bg-white p-2.5 rounded-lg border border-rose-100">
                <div className="col-span-6">
                  <input
                    type="text"
                    value={lt.testType}
                    onChange={(e) => {
                      const updated = [...consultForm.labTests];
                      updated[idx].testType = e.target.value;
                      setConsultForm({ ...consultForm, labTests: updated });
                    }}
                    placeholder="Test Name (e.g. ECG, Lipid Profile)"
                    className="w-full text-xs p-1.5 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
                <div className="col-span-4">
                  <input
                    type="number"
                    min="0"
                    step="50"
                    value={lt.charge}
                    onChange={(e) => {
                      const updated = [...consultForm.labTests];
                      updated[idx].charge = parseFloat(e.target.value) || 0;
                      setConsultForm({ ...consultForm, labTests: updated });
                    }}
                    placeholder="Charge ($)"
                    className="w-full text-xs p-1.5 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
                <div className="col-span-2 text-center">
                  <button
                    type="button"
                    onClick={() => removeLabTestRow(idx)}
                    className="text-rose-500 hover:text-rose-700 p-1"
                  >
                    <Trash className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsConsultModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Saving Transaction...' : 'Save Consultation (1 Transaction)'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Lab Result Entry Modal */}
      <Modal
        isOpen={isLabModalOpen}
        onClose={() => setIsLabModalOpen(false)}
        title="Enter Lab Test Result"
        subtitle={`Recording laboratory diagnostic results for ${selectedLabTest?.testId}`}
      >
        <form onSubmit={handleUpdateLabResult} className="space-y-4">
          <FormField
            label="Diagnostic Finding / Value"
            name="result"
            type="textarea"
            value={labResultData.result}
            onChange={(e) => setLabResultData({ ...labResultData, result: e.target.value })}
            placeholder="e.g. Hemoglobin: 11.2 g/dL (Below Reference Range 13.5-17.5)"
            required
          />

          <FormField
            label="Result Classification"
            name="resultStatus"
            type="select"
            value={labResultData.resultStatus}
            onChange={(e) => setLabResultData({ ...labResultData, resultStatus: e.target.value })}
            options={[
              { value: 'Normal', label: 'Normal (Within limits)' },
              { value: 'Abnormal', label: 'Abnormal (Requires Attention)' }
            ]}
            required
            helperText="Abnormal results trigger automated hospital safety alerts"
          />

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsLabModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-xl shadow-xs transition-colors"
            >
              {isSubmitting ? 'Recording...' : 'Record Result'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
