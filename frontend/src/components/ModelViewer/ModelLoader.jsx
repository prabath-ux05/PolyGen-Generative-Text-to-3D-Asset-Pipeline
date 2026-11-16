import { useState, useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

function ModelLoader({ url, wireframe = false, onLoaded, onError, onProgress }) {
  const [model, setModel] = useState(null)
  const groupRef = useRef(null)
  const wireframeRef = useRef(wireframe)

  useEffect(() => {
    wireframeRef.current = wireframe
  }, [wireframe])

  useEffect(() => {
    if (!url) {
      setModel(null)
      return
    }

    let isMounted = true
    let loadedObject = null

    // Determine loader type by file extension
    const cleanUrl = url.split('?')[0].toLowerCase()
    const isGLTF = cleanUrl.endsWith('.gltf') || cleanUrl.endsWith('.glb')

    if (onProgress) onProgress(10)

    const handleSuccess = (rawSceneOrObject) => {
      if (!isMounted) {
        disposeThreeObject(rawSceneOrObject)
        return
      }

      try {
        const obj = isGLTF ? rawSceneOrObject.scene : rawSceneOrObject
        loadedObject = obj

        let totalVertices = 0
        let totalTriangles = 0
        let meshCount = 0

        // Traverse meshes to compute metrics and apply default sleek materials
        obj.traverse((child) => {
          if (child.isMesh) {
            meshCount++
            const geometry = child.geometry

            if (geometry) {
              // Ensure normals exist for proper shading
              if (!geometry.attributes.normal) {
                geometry.computeVertexNormals()
              }

              const posAttr = geometry.attributes.position
              if (posAttr) {
                totalVertices += posAttr.count
              }

              if (geometry.index) {
                totalTriangles += geometry.index.count / 3
              } else if (posAttr) {
                totalTriangles += posAttr.count / 3
              }
            }

            // If OBJ has no material or standard white default, provide PolyGen PBR material
            if (!child.material || child.material.name === 'default' || !child.material.metalness) {
              child.material = new THREE.MeshStandardMaterial({
                color: new THREE.Color(0xa78bfa),
                roughness: 0.35,
                metalness: 0.6,
                wireframe: wireframeRef.current,
              })
            } else {
              child.material.wireframe = wireframeRef.current
            }

            child.castShadow = true
            child.receiveShadow = true
          }
        })

        // Auto-center and normalize scale
        const box = new THREE.Box3().setFromObject(obj)
        const size = box.getSize(new THREE.Vector3())
        const center = box.getCenter(new THREE.Vector3())

        // Offset to center
        obj.position.x = -center.x
        obj.position.y = -center.y
        obj.position.z = -center.z

        // Normalize scale to fit nicely in the view (approx 3.2 units)
        const maxDim = Math.max(size.x, size.y, size.z)
        const targetDim = 3.2
        const scaleFactor = maxDim > 0 ? targetDim / maxDim : 1

        const wrapperGroup = new THREE.Group()
        wrapperGroup.add(obj)
        wrapperGroup.scale.setScalar(scaleFactor)

        setModel(wrapperGroup)

        if (onProgress) onProgress(100)

        if (onLoaded) {
          onLoaded({
            url,
            format: isGLTF ? 'GLTF / GLB' : 'Wavefront OBJ',
            vertices: totalVertices,
            triangles: Math.round(totalTriangles),
            meshCount,
            dimensions: {
              x: (size.x * scaleFactor).toFixed(2),
              y: (size.y * scaleFactor).toFixed(2),
              z: (size.z * scaleFactor).toFixed(2),
            },
          })
        }
      } catch (err) {
        if (onError && isMounted) {
          onError(err.message || 'Error processing 3D mesh geometry.')
        }
      }
    }

    const handleLoadError = (err) => {
      if (!isMounted) return
      let msg = 'Failed to load model file.'
      if (err?.target?.status === 404 || (err?.message && err.message.includes('404'))) {
        msg = `File not found (404): ${url}`
      } else if (err?.message) {
        msg = err.message
      }
      if (onError) onError(msg)
    }

    const handleProgress = (xhr) => {
      if (!isMounted) return
      if (xhr && xhr.total > 0 && onProgress) {
        const percent = Math.round((xhr.loaded / xhr.total) * 100)
        onProgress(percent)
      }
    }

    // Execute loader
    if (isGLTF) {
      const gltfLoader = new GLTFLoader()
      gltfLoader.load(url, handleSuccess, handleProgress, handleLoadError)
    } else {
      const objLoader = new OBJLoader()
      objLoader.load(url, handleSuccess, handleProgress, handleLoadError)
    }

    return () => {
      isMounted = false
      if (loadedObject) {
        disposeThreeObject(loadedObject)
      }
    }
  }, [url, onError, onLoaded, onProgress])

  // Update wireframe mode without reloading geometry
  useEffect(() => {
    if (!model) return
    model.traverse((child) => {
      if (child.isMesh && child.material) {
        child.material.wireframe = wireframe
      }
    })
  }, [wireframe, model])

  if (!model) return null

  return (
    <group ref={groupRef}>
      <primitive object={model} />
    </group>
  )
}

function disposeThreeObject(obj) {
  if (!obj) return
  obj.traverse((child) => {
    if (child.geometry) {
      child.geometry.dispose()
    }
    if (child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach((mat) => mat.dispose())
      } else {
        child.material.dispose()
      }
    }
  })
}

export default ModelLoader
