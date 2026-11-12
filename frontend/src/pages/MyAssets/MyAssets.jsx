import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Grid, List, Search, Filter } from 'lucide-react'
import RecentAssets from '../../components/RecentAssets/RecentAssets.jsx'
import './MyAssets.css'

function MyAssets() {
  const [searchParams] = useSearchParams()
  const [viewMode, setViewMode] = useState('grid')
  const [searchVal, setSearchVal] = useState(() => searchParams.get('q') || '')

  useEffect(() => {
    const q = searchParams.get('q')
    if (q !== null) setSearchVal(q)
  }, [searchParams])

  return (
    <div className="my-assets-page">
      <div className="my-assets-header">
        <div>
          <h1 className="page-title">My Assets</h1>
          <p className="page-subtitle">Browse and manage all your generated 3D models.</p>
        </div>
        <div className="my-assets-actions">
          <div className="my-assets-search">
            <Search size={14} className="my-assets-search-icon" />
            <input
              className="input my-assets-search-input"
              placeholder="Search assets…"
              value={searchVal}
              onChange={e => setSearchVal(e.target.value)}
            />
          </div>
          <button className="btn btn-secondary btn-sm">
            <Filter size={13} />
            Filter
          </button>
          <div className="my-assets-view-toggle">
            <button
              className={`view-toggle-btn ${viewMode === 'grid' ? 'view-toggle-active' : ''}`}
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
            >
              <Grid size={15} />
            </button>
            <button
              className={`view-toggle-btn ${viewMode === 'list' ? 'view-toggle-active' : ''}`}
              onClick={() => setViewMode('list')}
              aria-label="List view"
            >
              <List size={15} />
            </button>
          </div>
        </div>
      </div>

      <RecentAssets limit={12} searchQuery={searchVal} viewMode={viewMode} />
    </div>
  )
}

export default MyAssets
