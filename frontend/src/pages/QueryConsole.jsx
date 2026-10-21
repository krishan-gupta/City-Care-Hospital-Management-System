import React, { useState, useEffect } from 'react';
import { Terminal, Play, Copy, Check, Info, Database, Layers, CheckCircle2 } from 'lucide-react';
import { getQueries, runNamedQuery, getPatients } from '../api';
import Loader from '../components/Loader';
import ErrorBanner from '../components/ErrorBanner';

export default function QueryConsole() {
  const [queries, setQueries] = useState([]);
  const [selectedQueryName, setSelectedQueryName] = useState('');
  const [paramId, setParamId] = useState('PAT-101');
  const [queryResult, setQueryResult] = useState(null);
  const [isLoadingQueries, setIsLoadingQueries] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setIsLoadingQueries(true);
    getQueries()
      .then((res) => {
        const list = res.data || [];
        setQueries(list);
        if (list.length > 0) {
          setSelectedQueryName(list[0].name);
        }
      })
      .catch((err) => setError(err.message || 'Failed to fetch ready-made queries.'))
      .finally(() => setIsLoadingQueries(false));

    getPatients({ page: 1, size: 5 })
      .then((res) => {
        const first = res.data?.items?.[0]?.patientId;
        if (first) setParamId(first);
      })
      .catch(() => {});
  }, []);

  const currentQuery = queries.find((q) => q.name === selectedQueryName) || queries[0];

  const handleRunQuery = async () => {
    if (!currentQuery) return;
    setIsRunning(true);
    setError(null);
    try {
      const res = await runNamedQuery(currentQuery.name, currentQuery.requiresId ? paramId : undefined);
      setQueryResult(res.data);
    } catch (err) {
      setError(err.message || 'Error executing Cypher query.');
      setQueryResult(null);
    } finally {
      setIsRunning(false);
    }
  };

  // Run automatically on first selection
  useEffect(() => {
    if (currentQuery) {
      handleRunQuery();
    }
  }, [selectedQueryName]);

  const copyCypher = () => {
    if (currentQuery?.cypher) {
      navigator.clipboard.writeText(currentQuery.cypher);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoadingQueries) return <Loader message="Loading ready-made Cypher queries..." />;

  // Dynamic columns from returned result rows
  const resultRows = queryResult?.data || [];
  const resultKeys = resultRows.length > 0 ? Object.keys(resultRows[0]) : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-slate-900 text-sky-400 rounded-xl shadow-xs">
              <Terminal className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Cypher Query Console
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Execute assignment-required Cypher queries directly against the Neo4j AuraDB graph.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-semibold px-3 py-1.5 bg-sky-50 text-sky-800 border border-sky-200 rounded-xl">
          <Database className="w-4 h-4 text-sky-600" />
          <span>Neo4j AuraDB Active</span>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={handleRunQuery} />

      {/* Query Selector and Parameter Input */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          <div className="md:col-span-8">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Choose Assignment Cypher Query ({queries.length} Ready-Made)
            </label>
            <select
              value={selectedQueryName}
              onChange={(e) => setSelectedQueryName(e.target.value)}
              className="w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              {queries.map((q) => (
                <option key={q.name} value={q.name}>
                  {q.title} ({q.name})
                </option>
              ))}
            </select>
          </div>

          {currentQuery?.requiresId && (
            <div className="md:col-span-4">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Query Parameter ($id)
              </label>
              <input
                type="text"
                value={paramId}
                onChange={(e) => setParamId(e.target.value)}
                placeholder="e.g. PAT-101"
                className="w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </div>
          )}
        </div>

        {/* Query Info Banner */}
        {currentQuery && (
          <div className="flex items-start space-x-2.5 p-3.5 bg-slate-50 rounded-xl border border-slate-200/70 text-xs text-slate-600">
            <Info className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900 block text-xs">{currentQuery.title}</strong>
              <p className="mt-0.5">{currentQuery.description}</p>
            </div>
          </div>
        )}

        {/* Cypher Viewer */}
        <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-slate-950">
          <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
              <span className="text-[11px] font-mono text-slate-400 ml-2">cypher_statement.cql</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={copyCypher}
                className="flex items-center space-x-1 text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded-md bg-slate-800/60 hover:bg-slate-800 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
              <button
                onClick={handleRunQuery}
                disabled={isRunning}
                className="flex items-center space-x-1.5 px-3 py-1 text-xs font-bold text-white bg-sky-600 hover:bg-sky-500 rounded-md shadow-xs transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isRunning ? 'Running...' : 'Execute'}</span>
              </button>
            </div>
          </div>
          <pre className="p-4 text-xs font-mono text-sky-300 overflow-x-auto whitespace-pre leading-relaxed">
            {currentQuery?.cypher}
          </pre>
        </div>
      </div>

      {/* Query Results Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-slate-500" />
            <h3 className="text-base font-bold text-slate-900">Result Dataset</h3>
          </div>
          <div className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-lg">
            Returned Rows: <strong className="text-slate-900">{queryResult?.rowCount ?? 0}</strong>
          </div>
        </div>

        <div className="overflow-x-auto">
          {isRunning ? (
            <div className="p-12 text-center text-slate-400">
              <Loader message="Running Cypher query on AuraDB..." />
            </div>
          ) : resultRows.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              Query returned 0 rows.
            </div>
          ) : (
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 tracking-wider border-b border-slate-100">
                <tr>
                  {resultKeys.map((key) => (
                    <th key={key} className="px-5 py-3">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {resultRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-50/70 transition-colors">
                    {resultKeys.map((key) => {
                      const val = row[key];
                      return (
                        <td key={key} className="px-5 py-3 text-xs">
                          {Array.isArray(val) ? (
                            <div className="flex flex-wrap gap-1">
                              {val.map((item, i) => (
                                <span
                                  key={i}
                                  className="bg-slate-100 text-slate-800 px-2 py-0.5 rounded text-[11px]"
                                >
                                  {typeof item === 'object' ? JSON.stringify(item) : String(item)}
                                </span>
                              ))}
                            </div>
                          ) : typeof val === 'object' && val !== null ? (
                            <pre className="text-[10px] bg-slate-50 p-1.5 rounded border border-slate-200 overflow-x-auto max-w-xs">
                              {JSON.stringify(val, null, 2)}
                            </pre>
                          ) : typeof val === 'number' ? (
                            <span className="font-mono font-medium text-slate-900">
                              {val.toLocaleString()}
                            </span>
                          ) : (
                            <span className="font-medium text-slate-800">
                              {val !== null && val !== undefined ? String(val) : '—'}
                            </span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
