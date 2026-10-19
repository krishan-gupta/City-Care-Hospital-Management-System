import React, { useState, useEffect } from 'react';
import {
  Users, UserCheck, Calendar, DollarSign, FileText, Activity, AlertCircle, ArrowUpRight
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import {
  getDashboardSummary, getDashboardBilling, getDashboardClaims, getDashboardDoctors
} from '../api';
import KpiCard from '../components/KpiCard';
import Loader from '../components/Loader';
import ErrorBanner from '../components/ErrorBanner';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [billingData, setBillingData] = useState(null);
  const [claimsData, setClaimsData] = useState(null);
  const [doctorsData, setDoctorsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sumRes, billRes, claimsRes, docsRes] = await Promise.all([
        getDashboardSummary(),
        getDashboardBilling(),
        getDashboardClaims(),
        getDashboardDoctors()
      ]);
      setSummary(sumRes.data);
      setBillingData(billRes.data);
      setClaimsData(claimsRes.data);
      setDoctorsData(docsRes.data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (isLoading) return <Loader message="Loading hospital analytics & KPIs..." />;

  const PIE_COLORS = ['#38bdf8', '#fbbf24', '#f87171', '#a78bfa', '#34d399'];

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Hospital Operations Dashboard
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Real-time metrics, revenue streams, and doctor workload from Neo4j AuraDB.
        </p>
      </div>

      <ErrorBanner message={error} onRetry={fetchDashboardData} />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Patients"
          value={summary?.totalPatients ?? 0}
          icon={Users}
          color="green"
          subtitle="Registered in system"
        />
        <KpiCard
          title="Active Doctors"
          value={summary?.totalDoctors ?? 0}
          icon={UserCheck}
          color="blue"
          subtitle="Across 7 departments"
        />
        <KpiCard
          title="Total Appointments"
          value={summary?.totalAppointments ?? 0}
          icon={Calendar}
          color="purple"
          subtitle={`${summary?.appointmentsToday ?? 0} booked for today`}
        />
        <KpiCard
          title="Total Revenue"
          value={`$${Number(summary?.totalRevenue || 0).toLocaleString()}`}
          icon={DollarSign}
          color="amber"
          subtitle={`Avg: $${billingData?.stats?.average ? Number(billingData.stats.average).toFixed(0) : '0'} / bill`}
        />
      </div>

      {/* Secondary Quick Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Pending Claims</span>
            <p className="text-xl font-bold text-slate-800">{summary?.pendingClaims ?? 0}</p>
          </div>
          <FileText className="w-8 h-8 text-indigo-500 bg-indigo-50 p-1.5 rounded-lg" />
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Abnormal Lab Results</span>
            <p className="text-xl font-bold text-rose-600">{summary?.abnormalLabResults ?? 0}</p>
          </div>
          <AlertCircle className="w-8 h-8 text-rose-500 bg-rose-50 p-1.5 rounded-lg" />
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Highest Single Bill</span>
            <p className="text-xl font-bold text-emerald-600">
              ${billingData?.stats?.highest ? Number(billingData.stats.highest).toLocaleString() : '0'}
            </p>
          </div>
          <Activity className="w-8 h-8 text-emerald-500 bg-emerald-50 p-1.5 rounded-lg" />
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Revenue Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Revenue by Department</h3>
              <p className="text-xs text-slate-500">Total billings generated across hospital units</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-sky-50 text-sky-700 rounded-lg">
              Live Aggregation
            </span>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={billingData?.revenueByDepartment || []}
                margin={{ top: 10, right: 10, left: 10, bottom: 25 }}
              >
                <XAxis
                  dataKey="department"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  angle={-20}
                  textAnchor="end"
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="revenue" fill="#0284c7" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Claim Status Pie Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Insurance Claims Status</h3>
              <p className="text-xs text-slate-500">Distribution of claim processing states</p>
            </div>
          </div>
          <div className="h-72 w-full flex items-center justify-center">
            {claimsData?.byStatus && claimsData.byStatus.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={claimsData.byStatus}
                    dataKey="count"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={95}
                    innerRadius={55}
                    paddingAngle={4}
                  >
                    {claimsData.byStatus.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val, name, item) => [
                      `${val} claims ($${Number(item.payload.totalAmount || 0).toLocaleString()})`,
                      name
                    ]}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                  />
                  <Legend verticalAlign="bottom" wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-400 text-sm">No claim records available</div>
            )}
          </div>
        </div>
      </div>

      {/* Doctor Workload Table & Above-Average Analysis */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
          <div>
            <h3 className="text-base font-bold text-slate-900">Doctor Patient Load & Above-Average Benchmark</h3>
            <p className="text-xs text-slate-500">Calculates unique patient reach against the hospital average</p>
          </div>
          <span className="text-xs font-semibold px-3 py-1 bg-purple-50 text-purple-700 rounded-lg self-start sm:self-auto">
            Nested Aggregation Query
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-100">
              <tr>
                <th className="px-4 py-3">Doctor</th>
                <th className="px-4 py-3">Department</th>
                <th className="px-4 py-3 text-center">Unique Patients</th>
                <th className="px-4 py-3 text-center">Hospital Avg</th>
                <th className="px-4 py-3 text-right">Performance Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {doctorsData.map((doc, idx) => (
                <tr key={doc.empId || idx} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-4 py-3.5 font-semibold text-slate-900">Dr. {doc.doctor}</td>
                  <td className="px-4 py-3.5">{doc.department || 'General'}</td>
                  <td className="px-4 py-3.5 text-center font-bold text-slate-800">{doc.patients}</td>
                  <td className="px-4 py-3.5 text-center text-slate-500">{doc.averagePatients}</td>
                  <td className="px-4 py-3.5 text-right">
                    {doc.isAboveAverage ? (
                      <span className="inline-flex items-center space-x-1 px-2.5 py-1 text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full">
                        <ArrowUpRight className="w-3.5 h-3.5" />
                        <span>Above Average</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-1 text-xs font-medium bg-slate-100 text-slate-600 rounded-full">
                        Standard
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
