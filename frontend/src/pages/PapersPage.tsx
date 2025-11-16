import { useState } from 'react'
import { usePapers } from '../hooks/usePapers'

export default function PapersPage() {
  const { papers, isLoading, searchMutation, uploadMutation, createMutation, deleteMutation } = usePapers()
  const [activeTab, setActiveTab] = useState<'list' | 'search' | 'upload'>('list')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploadAuthors, setUploadAuthors] = useState('')

  const handleSearch = async () => {
    try {
      const response = await searchMutation.mutateAsync(searchQuery)
      setSearchResults(response.data)
    } catch (error) {
      console.error('검색 실패:', error)
    }
  }

  const handleSavePaper = async (paper: any) => {
    try {
      await createMutation.mutateAsync(paper)
      alert('논문이 저장되었습니다')
    } catch (error) {
      console.error('논문 저장 실패:', error)
      alert('논문 저장에 실패했습니다')
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) {
      alert('파일을 선택해주세요')
      return
    }

    try {
      await uploadMutation.mutateAsync({
        file: selectedFile,
        title: uploadTitle,
        authors: uploadAuthors,
      })
      alert('논문이 업로드되었습니다')
      setSelectedFile(null)
      setUploadTitle('')
      setUploadAuthors('')
      setActiveTab('list')
    } catch (error) {
      console.error('업로드 실패:', error)
      alert('업로드에 실패했습니다')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return

    try {
      await deleteMutation.mutateAsync(id)
      alert('논문이 삭제되었습니다')
    } catch (error) {
      console.error('삭제 실패:', error)
      alert('삭제에 실패했습니다')
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">논문 관리</h1>

      {/* 탭 네비게이션 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('list')}
            className={`${
              activeTab === 'list'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            내 논문 ({papers?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`${
              activeTab === 'search'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            PubMed 검색
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`${
              activeTab === 'upload'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            PDF 업로드
          </button>
        </nav>
      </div>

      {/* 내 논문 목록 */}
      {activeTab === 'list' && (
        <div className="bg-white shadow rounded-lg">
          {isLoading ? (
            <div className="p-6 text-center">로딩 중...</div>
          ) : papers && papers.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {papers.map((paper: any) => (
                <li key={paper.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">{paper.title}</h3>
                      {paper.authors && (
                        <p className="mt-1 text-sm text-gray-500">{paper.authors}</p>
                      )}
                      {paper.journal && (
                        <p className="mt-1 text-sm text-gray-500">
                          {paper.journal}
                          {paper.publication_date && ` · ${new Date(paper.publication_date).getFullYear()}`}
                        </p>
                      )}
                      {paper.abstract && (
                        <p className="mt-2 text-sm text-gray-600 line-clamp-2">{paper.abstract}</p>
                      )}
                    </div>
                    <button
                      onClick={() => handleDelete(paper.id)}
                      className="ml-4 text-red-600 hover:text-red-800"
                    >
                      삭제
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-6 text-center text-gray-500">
              저장된 논문이 없습니다. PubMed에서 검색하거나 PDF를 업로드하세요.
            </div>
          )}
        </div>
      )}

      {/* PubMed 검색 */}
      {activeTab === 'search' && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex gap-4 mb-6">
            <input
              type="text"
              placeholder="검색어 입력 (예: cancer immunotherapy)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleSearch}
              disabled={searchMutation.isPending}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {searchMutation.isPending ? '검색 중...' : '검색'}
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">검색 결과 ({searchResults.length})</h3>
              {searchResults.map((paper: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900">{paper.title}</h4>
                  {paper.authors && (
                    <p className="mt-1 text-sm text-gray-500">{paper.authors}</p>
                  )}
                  {paper.journal && (
                    <p className="mt-1 text-sm text-gray-500">{paper.journal}</p>
                  )}
                  {paper.abstract && (
                    <p className="mt-2 text-sm text-gray-600">{paper.abstract}</p>
                  )}
                  <button
                    onClick={() => handleSavePaper(paper)}
                    disabled={createMutation.isPending}
                    className="mt-3 px-4 py-2 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700 disabled:opacity-50"
                  >
                    내 라이브러리에 저장
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* PDF 업로드 */}
      {activeTab === 'upload' && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDF 파일 선택
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-500">선택된 파일: {selectedFile.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제목 (선택사항)
              </label>
              <input
                type="text"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="논문 제목"
                className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                저자 (선택사항)
              </label>
              <input
                type="text"
                value={uploadAuthors}
                onChange={(e) => setUploadAuthors(e.target.value)}
                placeholder="저자명"
                className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <button
              onClick={handleFileUpload}
              disabled={!selectedFile || uploadMutation.isPending}
              className="w-full px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploadMutation.isPending ? '업로드 중...' : '업로드'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
