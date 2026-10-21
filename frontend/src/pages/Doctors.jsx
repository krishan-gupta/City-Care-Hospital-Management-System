import React, { useState, useEffect } from 'react';
import { UserCheck, Building2, Phone, Mail, Award, Users, Filter, CheckCircle2 } from 'lucide-react';
import { getDoctors, getDepartments } from '../api';
import Loader from '../components/Loader';
import ErrorBanner from '../components/ErrorBanner';

export default function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [docsRes, deptsRes] = await Promise.all([
        getDoctors({ department: selectedDept || undefined }),
        getDepartments()
      ]);
      setDoctors(docsRes.data || []);
      setDepartments(deptsRes.data || []);
    } catch (err) {
      setError(err.message || 'Failed to load doctors and departments.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedDept]);

  if (isLoading) return <Loader message="Loading medical staff and department records..." />;

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Doctors & Departments
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Specialist medical staff, department assignments, and clinical patient workload.
        </p>
      </div>

      <ErrorBanner message={error} onRetry={fetchData} />

      {/* Departments Overview Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-2">
            <Building2 className="w-4 h-4 text-sky-600" />
            <span>Hospital Departments ({departments.length})</span>
          </h2>
          <span className="text-xs text-slate-400">Click a department to filter doctors</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <button
            onClick={() => setSelectedDept('')}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              selectedDept === ''
                ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
                : 'bg-white text-slate-700 border-slate-200/80 hover:border-slate-300'
            }`}
          >
            <span className="text-xs font-semibold block truncate">All Departments</span>
            <span className="text-lg font-bold block mt-1">{doctors.length} docs</span>
          </button>
          {departments.map((dept) => (
            <button
              key={dept.deptId || dept.name}
              onClick={() => setSelectedDept(dept.name)}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                selectedDept === dept.name
                  ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
                  : 'bg-white text-slate-700 border-slate-200/80 hover:border-slate-300'
              }`}
            >
              <span className="text-xs font-semibold block truncate">{dept.name}</span>
              <span className={`text-lg font-bold block mt-1 ${selectedDept === dept.name ? 'text-white' : 'text-sky-700'}`}>
                {dept.doctorCount} {dept.doctorCount === 1 ? 'doc' : 'docs'}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Doctors Grid */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <UserCheck className="w-5 h-5 text-sky-600" />
            <h2 className="text-lg font-bold text-slate-900">
              Medical Practitioners {selectedDept && <span className="text-slate-400 font-normal">in {selectedDept}</span>}
            </h2>
          </div>
          <div className="text-xs text-slate-500 font-medium">
            Showing <strong className="text-slate-800">{doctors.length}</strong> doctors
          </div>
        </div>

        {doctors.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400">
            No doctors found for this filter.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {doctors.map((doc) => (
              <div
                key={doc.empId}
                className="bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition-all p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-700 font-bold flex items-center justify-center text-base border border-sky-100">
                        Dr
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-slate-900">
                          {doc.name?.startsWith('Dr.') ? doc.name : `Dr. ${doc.name}`}
                        </h3>
                        <span className="text-xs font-semibold text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md border border-sky-100 inline-block mt-0.5">
                          {doc.specialization || 'General Practice'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 space-y-2 text-xs text-slate-600">
                    <div className="flex items-center space-x-2">
                      <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>Dept: <strong className="text-slate-800">{doc.department || 'General'}</strong></span>
                    </div>
                    {doc.hospitalBranch && (
                      <div className="flex items-center space-x-2">
                        <Award className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>Branch: <strong className="text-slate-800">{doc.hospitalBranch}</strong></span>
                      </div>
                    )}
                    {doc.experience && (
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>Experience: <strong className="text-slate-800">{doc.experience} years</strong></span>
                      </div>
                    )}
                    {doc.phone && (
                      <div className="flex items-center space-x-2">
                        <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span>{doc.phone}</span>
                      </div>
                    )}
                    {doc.email && (
                      <div className="flex items-center space-x-2">
                        <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="truncate">{doc.email}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Patient Reach Badge */}
                <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">{doc.empId}</span>
                  <div className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-full text-xs font-semibold">
                    <Users className="w-3.5 h-3.5" />
                    <span>{doc.patientCount ?? 0} unique patients</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
