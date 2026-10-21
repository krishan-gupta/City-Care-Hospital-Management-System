import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import {
  ArrowLeft, GitFork, User, Calendar, Stethoscope, Pill, FlaskConical, DollarSign, Shield, Info, RefreshCw
} from 'lucide-react';
import { getPatientJourney, getPatients } from '../api';
import Loader from '../components/Loader';
import ErrorBanner from '../components/ErrorBanner';

const NODE_COLORS = {
  Patient: '#10b981',        // Emerald
  Doctor: '#0284c7',         // Sky
  Department: '#0d9488',     // Teal
  Appointment: '#8b5cf6',    // Purple
  Consultation: '#06b6d4',   // Cyan
  Treatment: '#ec4899',      // Pink
  Prescription: '#f97316',   // Orange
  LabTest: '#f43f5e',        // Rose
  Bill: '#f59e0b',           // Amber
  InsuranceClaim: '#6366f1', // Indigo
};

export default function PatientJourney() {
  const { id } = useParams();
  const navigate = useNavigate();
  const fgRef = useRef();

  const [currentId, setCurrentId] = useState(id && id !== 'P029' ? id : '');
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [recentPatients, setRecentPatients] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch recent patients for quick switcher dropdown & auto-selection
  useEffect(() => {
    let isMounted = true;
    getPatients({ page: 1, size: 50 })
      .then((res) => {
        if (!isMounted) return;
        const patients = res.data?.items || [];
        setRecentPatients(patients);

        if (patients.length > 0) {
          // If no id, or legacy 'P029', or id not in current loaded patient list
          const hasValidId = id && id !== 'P029' && patients.some((p) => p.patientId === id);
          if (!hasValidId) {
            const firstPatientId = patients[0].patientId;
            setCurrentId(firstPatientId);
            navigate(`/patients/${firstPatientId}/journey`, { replace: true });
          }
        }
      })
      .catch((err) => {
        if (isMounted) console.error('Error fetching patients for switcher:', err);
      });

    return () => {
      isMounted = false;
    };
  }, [id, navigate]);

  const fetchJourney = async (patientId) => {
    if (!patientId || patientId === 'P029') return;
    setIsLoading(true);
    setError(null);
    setSelectedNode(null);
    try {
      const res = await getPatientJourney(patientId);
      // Clone nodes and links so force-graph can mutate coordinates
      const nodes = (res.data.nodes || []).map((n) => ({ ...n }));
      const links = (res.data.links || []).map((l) => ({ ...l }));
      setGraphData({ nodes, links });

      // Automatically select the root patient node
      const rootPatient = nodes.find((n) => n.label === 'Patient');
      if (rootPatient) setSelectedNode(rootPatient);
    } catch (err) {
      setError(err.message || 'Failed to fetch patient journey graph.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id && id !== 'P029') {
      setCurrentId(id);
    }
  }, [id]);

  useEffect(() => {
    if (currentId && currentId !== 'P029') {
      fetchJourney(currentId);
    }
  }, [currentId]);

  const handlePatientChange = (newId) => {
    setCurrentId(newId);
    navigate(`/patients/${newId}/journey`);
  };

  // Custom node drawing with text and colored halo
  const drawNode = useCallback((node, ctx, globalScale) => {
    const color = NODE_COLORS[node.label] || '#94a3b8';
    const isSelected = selectedNode && selectedNode.id === node.id;
    const r = node.label === 'Patient' ? 8 : 6;

    // Outer selection ring
    if (isSelected) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, r + 4, 0, 2 * Math.PI, false);
      ctx.fillStyle = 'rgba(2, 132, 199, 0.25)';
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#0284c7';
      ctx.stroke();
    }

    // Node body
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();

    // Node label text on canvas if zoomed in enough
    if (globalScale > 0.8) {
      const label = node.name || node.id;
      const fontSize = Math.max(10 / globalScale, 3);
      ctx.font = `${fontSize}px Inter, sans-serif`;
      ctx.fillStyle = '#1e293b';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(label.length > 20 ? label.slice(0, 18) + '...' : label, node.x, node.y + r + 2);
    }
  }, [selectedNode]);

  return (
    <div className="space-y-6">
      {/* Top Header & Patient Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/patients')}
            className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <GitFork className="w-5 h-5 text-emerald-600" />
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                Patient Journey Interactive Graph
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Live Neo4j graph traversal of appointments, doctors, prescriptions, lab tests, and claims.
            </p>
          </div>
        </div>

        {/* Patient Switcher */}
        <div className="flex items-center space-x-3">
          <label className="text-xs font-semibold text-slate-500 uppercase">Select Patient:</label>
          <select
            value={currentId}
            onChange={(e) => handlePatientChange(e.target.value)}
            className="px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-xl font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            {recentPatients.map((p, idx) => (
              <option key={`${p.patientId}-${idx}`} value={p.patientId}>
                {p.patientId} - {p.name} ({p.gender}, {p.age ? `${p.age}y` : ''})
              </option>
            ))}
          </select>
          <button
            onClick={() => fetchJourney(currentId)}
            className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors"
            title="Refresh graph"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={() => fetchJourney(currentId)} />

      {/* Legend */}
      <div className="bg-white px-5 py-3 rounded-xl border border-slate-200/80 shadow-2xs flex flex-wrap items-center gap-3 text-xs font-medium">
        <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">Node Legend:</span>
        {Object.entries(NODE_COLORS).map(([label, color]) => (
          <div key={label} className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-slate-700">{label}</span>
          </div>
        ))}
      </div>

      {/* Graph and Side Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Force-directed Graph Canvas */}
        <div className="lg:col-span-2 bg-slate-900 rounded-2xl border border-slate-800 shadow-md relative overflow-hidden min-h-[550px] flex items-center justify-center">
          {isLoading ? (
            <Loader message="Rendering patient knowledge graph..." />
          ) : graphData.nodes.length === 0 ? (
            <div className="text-slate-400 text-sm p-8 text-center">
              No graph relationships found for patient {currentId}.
            </div>
          ) : (
            <>
              <ForceGraph2D
                ref={fgRef}
                graphData={graphData}
                nodeCanvasObject={drawNode}
                nodePointerAreaPaint={(node, color, ctx) => {
                  ctx.fillStyle = color;
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false);
                  ctx.fill();
                }}
                linkDirectionalArrowLength={4}
                linkDirectionalArrowRelPos={1}
                linkColor={() => '#475569'}
                linkWidth={1.5}
                linkCurvature={0.15}
                linkLabel={(link) => link.type}
                onNodeClick={(node) => setSelectedNode(node)}
                cooldownTicks={100}
                onEngineStop={() => fgRef.current?.zoomToFit(400, 40)}
                width={700}
                height={550}
              />
              <div className="absolute bottom-3 left-3 bg-slate-950/70 backdrop-blur-xs text-[11px] text-slate-300 px-3 py-1.5 rounded-lg border border-slate-800">
                Nodes: <strong className="text-emerald-400">{graphData.nodes.length}</strong> | Links:{' '}
                <strong className="text-sky-400">{graphData.links.length}</strong> | Click a node to view details
              </div>
            </>
          )}
        </div>

        {/* Node Properties & Text Inspector Panel */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between overflow-hidden">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Info className="w-4 h-4 text-sky-600" />
                <h3 className="text-sm font-bold text-slate-900">Entity Details</h3>
              </div>
              {selectedNode && (
                <span
                  className="px-2.5 py-0.5 rounded-full text-xs font-bold text-white shadow-2xs"
                  style={{ backgroundColor: NODE_COLORS[selectedNode.label] || '#64748b' }}
                >
                  {selectedNode.label}
                </span>
              )}
            </div>

            {selectedNode ? (
              <div className="mt-4 space-y-4">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Name / Title</span>
                  <p className="text-base font-bold text-slate-900 mt-0.5">{selectedNode.name}</p>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Properties</span>
                  <div className="bg-slate-50 rounded-xl p-3 divide-y divide-slate-100 border border-slate-200/70 text-xs max-h-72 overflow-y-auto">
                    {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
                      <div key={k} className="py-2 flex items-start justify-between gap-2">
                        <span className="font-semibold text-slate-600 font-mono">{k}:</span>
                        <span className="text-slate-800 text-right font-medium break-all">
                          {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-slate-400 text-sm">
                Click any node in the graph to inspect its properties.
              </div>
            )}
          </div>

          {/* Quick Stats Summary */}
          <div className="pt-4 mt-6 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between">
            <span>Graph ID: <strong className="text-slate-800">{currentId}</strong></span>
            <button
              onClick={() => fgRef.current?.zoomToFit(400, 30)}
              className="text-sky-600 hover:text-sky-800 font-semibold"
            >
              Reset View
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
