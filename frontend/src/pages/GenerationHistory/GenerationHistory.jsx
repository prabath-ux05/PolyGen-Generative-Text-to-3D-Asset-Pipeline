import React from 'react'
import { Calendar, Download, Eye } from 'lucide-react'
import { mockHistory } from '../../data/mockData.js'
import './GenerationHistory.css'

const statusColors = {
  completed: 'green',
  processing: 'yellow',
  failed: 'red',
}

function GenerationHistory() {
  return (
    <div className="history-page">
      <div className="history-header">
        <div>
          <h1 className="page-title">Generation History</h1>
          <p className="page-subtitle">A complete log of all your 3D generation jobs.</p>
        </div>
        <button className="btn btn-secondary btn-sm">
          <Calendar size={13} />
          Filter by Date
        </button>
      </div>

      <div className="history-table-wrap card">
        <table className="history-table">
          <thead>
            <tr>
              <th>Asset Name</th>
              <th>Prompt</th>
              <th>Status</th>
              <th>Format</th>
              <th>Polygons</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {mockHistory.map(asset => (
              <tr key={asset.id} className="history-row">
                <td>
                  <div className="history-asset-name">
                    <div
                      className="history-thumb"
                      style={{ background: asset.thumbnailColor + '33', borderColor: asset.thumbnailColor + '55' }}
                    />
                    {asset.name}
                  </div>
                </td>
                <td className="history-prompt-cell">
                  <span title={asset.prompt}>
                    {asset.prompt.length > 50 ? asset.prompt.slice(0, 50) + '…' : asset.prompt}
                  </span>
                </td>
                <td>
                  <span className={`badge badge-${statusColors[asset.status]}`}>
                    {asset.status.charAt(0).toUpperCase() + asset.status.slice(1)}
                  </span>
                </td>
                <td className="history-mono">{asset.format}</td>
                <td className="history-mono">{asset.polygons}</td>
                <td className="history-date">
                  {new Date(asset.createdAt).toLocaleDateString('en-US', {
                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                  })}
                </td>
                <td>
                  <div className="history-actions">
                    <button className="btn btn-ghost btn-sm" disabled={asset.status !== 'completed'} aria-label="Preview">
                      <Eye size={13} />
                    </button>
                    <button className="btn btn-ghost btn-sm" disabled={asset.status !== 'completed'} aria-label="Download">
                      <Download size={13} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default GenerationHistory
