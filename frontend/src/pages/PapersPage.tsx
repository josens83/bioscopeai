import { useState, useRef } from 'react'
import { usePapers } from '../hooks/usePapers'
import {
  Card,
  CardHeader,
  CardContent,
  Button,
  IconButton,
  Input,
  SearchInput,
  Badge,
  SkeletonPaperCard,
  EmptyPapers,
  EmptySearchResults,
  Modal,
  ConfirmModal,
  DocumentIcon,
  SearchIcon,
  CloudArrowUpIcon,
  TrashIcon,
  PlusIcon,
  BookOpenIcon,
  ExternalLinkIcon,
  CalendarIcon,
  UserIcon,
  FolderIcon,
} from '../components/ui'

type Tab = 'list' | 'search' | 'upload'

interface TabItem {
  id: Tab
  label: string
  icon: typeof DocumentIcon
}

export default function PapersPage() {
  const { papers, isLoading, searchMutation, uploadMutation, createMutation, deleteMutation } = usePapers()
  const [activeTab, setActiveTab] = useState<Tab>('list')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploadAuthors, setUploadAuthors] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; title: string } | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const tabs: TabItem[] = [
    { id: 'list', label: `내 논문 (${papers?.length || 0})`, icon: FolderIcon },
    { id: 'search', label: 'PubMed 검색', icon: SearchIcon },
    { id: 'upload', label: 'PDF 업로드', icon: CloudArrowUpIcon },
  ]

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
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
    } catch (error) {
      console.error('논문 저장 실패:', error)
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return

    try {
      await uploadMutation.mutateAsync({
        file: selectedFile,
        title: uploadTitle,
        authors: uploadAuthors,
      })
      setSelectedFile(null)
      setUploadTitle('')
      setUploadAuthors('')
      setActiveTab('list')
    } catch (error) {
      console.error('업로드 실패:', error)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      setDeleteTarget(null)
    } catch (error) {
      console.error('삭제 실패:', error)
    }
  }

  // Drag and Drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 페이지 헤더 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
            논문 관리
          </h1>
          <p className="mt-1 text-surface-500 dark:text-surface-400">
            논문을 검색하고 라이브러리를 관리하세요
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<PlusIcon size={18} />}
          onClick={() => setActiveTab('upload')}
        >
          논문 추가
        </Button>
      </div>

      {/* 탭 네비게이션 */}
      <div className="border-b border-surface-200 dark:border-surface-700">
        <nav className="flex gap-1 -mb-px">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                  ${isActive
                    ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 hover:border-surface-300 dark:hover:border-surface-600'
                  }
                `}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* 내 논문 목록 */}
      {activeTab === 'list' && (
        <div>
          {isLoading ? (
            <div className="grid gap-4">
              {[1, 2, 3].map((i) => (
                <SkeletonPaperCard key={i} />
              ))}
            </div>
          ) : papers && papers.length > 0 ? (
            <div className="grid gap-4">
              {papers.map((paper: any) => (
                <Card key={paper.id} className="group hover:shadow-md transition-shadow">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4 min-w-0 flex-1">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 rounded-xl bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                            <BookOpenIcon size={24} className="text-brand-600 dark:text-brand-400" />
                          </div>
                        </div>
                        <div className="min-w-0 flex-1">
                          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100 line-clamp-2">
                            {paper.title}
                          </h3>
                          {paper.authors && (
                            <div className="flex items-center gap-1.5 mt-2 text-sm text-surface-500 dark:text-surface-400">
                              <UserIcon size={14} />
                              <span className="line-clamp-1">{paper.authors}</span>
                            </div>
                          )}
                          <div className="flex flex-wrap items-center gap-3 mt-2">
                            {paper.journal && (
                              <Badge variant="secondary" size="sm">
                                {paper.journal}
                              </Badge>
                            )}
                            {paper.publication_date && (
                              <span className="flex items-center gap-1 text-xs text-surface-400">
                                <CalendarIcon size={12} />
                                {new Date(paper.publication_date).getFullYear()}
                              </span>
                            )}
                          </div>
                          {paper.abstract && (
                            <p className="mt-3 text-sm text-surface-600 dark:text-surface-400 line-clamp-2">
                              {paper.abstract}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {paper.pubmed_id && (
                          <IconButton
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/${paper.pubmed_id}`, '_blank')}
                            title="PubMed에서 보기"
                          >
                            <ExternalLinkIcon size={18} />
                          </IconButton>
                        )}
                        <IconButton
                          variant="ghost"
                          size="sm"
                          className="text-error-500 hover:bg-error-50 dark:hover:bg-error-900/20"
                          onClick={() => setDeleteTarget({ id: paper.id, title: paper.title })}
                          title="삭제"
                        >
                          <TrashIcon size={18} />
                        </IconButton>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12">
                <EmptyPapers />
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* PubMed 검색 */}
      {activeTab === 'search' && (
        <div className="space-y-6">
          <Card>
            <CardContent className="p-5">
              <div className="flex gap-3">
                <div className="flex-1">
                  <SearchInput
                    placeholder="검색어 입력 (예: cancer immunotherapy, CRISPR gene editing)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <Button
                  variant="primary"
                  onClick={handleSearch}
                  loading={searchMutation.isPending}
                  leftIcon={<SearchIcon size={18} />}
                >
                  검색
                </Button>
              </div>
              <p className="mt-2 text-xs text-surface-400">
                PubMed에서 생물의학 논문을 검색합니다. 검색어는 영문으로 입력해주세요.
              </p>
            </CardContent>
          </Card>

          {searchResults.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
                  검색 결과 ({searchResults.length})
                </h3>
              </div>
              {searchResults.map((paper: any, index: number) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-5">
                    <h4 className="font-semibold text-surface-900 dark:text-surface-100">
                      {paper.title}
                    </h4>
                    {paper.authors && (
                      <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
                        {paper.authors}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {paper.journal && (
                        <Badge variant="secondary" size="sm">{paper.journal}</Badge>
                      )}
                      {paper.publication_date && (
                        <Badge variant="secondary" size="sm">
                          {new Date(paper.publication_date).getFullYear()}
                        </Badge>
                      )}
                    </div>
                    {paper.abstract && (
                      <p className="mt-3 text-sm text-surface-600 dark:text-surface-400 line-clamp-3">
                        {paper.abstract}
                      </p>
                    )}
                    <div className="mt-4 flex items-center gap-3">
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleSavePaper(paper)}
                        loading={createMutation.isPending}
                        leftIcon={<PlusIcon size={16} />}
                      >
                        라이브러리에 추가
                      </Button>
                      {paper.pubmed_id && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/${paper.pubmed_id}`, '_blank')}
                          rightIcon={<ExternalLinkIcon size={16} />}
                        >
                          PubMed에서 보기
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : searchMutation.isSuccess && searchResults.length === 0 ? (
            <Card>
              <CardContent className="py-12">
                <EmptySearchResults />
              </CardContent>
            </Card>
          ) : null}
        </div>
      )}

      {/* PDF 업로드 */}
      {activeTab === 'upload' && (
        <Card>
          <CardHeader
            title="PDF 논문 업로드"
            subtitle="PDF 파일을 업로드하면 AI가 자동으로 분석합니다"
          />
          <CardContent className="space-y-6">
            {/* Drag & Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`
                relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                transition-all duration-200
                ${isDragging
                  ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20'
                  : selectedFile
                    ? 'border-success-500 bg-success-50 dark:bg-success-900/20'
                    : 'border-surface-300 dark:border-surface-600 hover:border-brand-400 hover:bg-surface-50 dark:hover:bg-surface-800'
                }
              `}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="hidden"
              />
              <div className="flex flex-col items-center gap-3">
                <div className={`
                  w-14 h-14 rounded-xl flex items-center justify-center
                  ${selectedFile ? 'bg-success-100 dark:bg-success-900/30' : 'bg-surface-100 dark:bg-surface-800'}
                `}>
                  {selectedFile ? (
                    <DocumentIcon size={28} className="text-success-600 dark:text-success-400" />
                  ) : (
                    <CloudArrowUpIcon size={28} className="text-surface-400" />
                  )}
                </div>
                {selectedFile ? (
                  <>
                    <p className="font-medium text-surface-900 dark:text-surface-100">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-surface-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedFile(null)
                      }}
                    >
                      다른 파일 선택
                    </Button>
                  </>
                ) : (
                  <>
                    <div>
                      <p className="font-medium text-surface-900 dark:text-surface-100">
                        파일을 드래그하거나 클릭하여 업로드
                      </p>
                      <p className="mt-1 text-sm text-surface-500">
                        PDF 파일만 지원됩니다 (최대 50MB)
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* 메타데이터 입력 */}
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label="논문 제목"
                placeholder="논문 제목을 입력하세요 (선택사항)"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                hint="입력하지 않으면 AI가 자동으로 추출합니다"
              />
              <Input
                label="저자"
                placeholder="저자명을 입력하세요 (선택사항)"
                value={uploadAuthors}
                onChange={(e) => setUploadAuthors(e.target.value)}
                hint="여러 명은 쉼표로 구분"
              />
            </div>

            {/* 업로드 버튼 */}
            <div className="flex justify-end">
              <Button
                variant="primary"
                size="lg"
                onClick={handleFileUpload}
                disabled={!selectedFile}
                loading={uploadMutation.isPending}
                leftIcon={<CloudArrowUpIcon size={20} />}
              >
                업로드
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 삭제 확인 모달 */}
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="논문 삭제"
        message={`"${deleteTarget?.title}"을(를) 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`}
        confirmText="삭제"
        variant="danger"
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
