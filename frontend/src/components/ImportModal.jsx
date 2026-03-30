import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { Upload, FileSpreadsheet, X, Check, AlertTriangle, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from './ui/dialog';
import { ScrollArea } from './ui/scroll-area';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ImportModal({ open, onClose, onSuccess }) {
    const [step, setStep] = useState('upload'); // upload, preview, importing, done
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [importing, setImporting] = useState(false);
    const [progress, setProgress] = useState(0);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    const reset = () => {
        setStep('upload');
        setFile(null);
        setPreview(null);
        setImporting(false);
        setProgress(0);
        setResult(null);
        setError(null);
    };

    const handleClose = () => {
        reset();
        onClose();
    };

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFile = async (selectedFile) => {
        const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!validTypes.includes(selectedFile.type) && !selectedFile.name.match(/\.(csv|xlsx|xls)$/i)) {
            setError('Please upload a CSV or Excel file');
            return;
        }

        setFile(selectedFile);
        setError(null);

        // Get preview
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            const res = await axios.post(`${API_URL}/api/leads/import/preview`, formData, {
                withCredentials: true,
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            setPreview(res.data);
            setStep('preview');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to read file');
        }
    };

    const handleImport = async () => {
        if (!file) return;

        setStep('importing');
        setImporting(true);
        setProgress(10);

        try {
            const formData = new FormData();
            formData.append('file', file);
            
            // Simulate progress
            const progressInterval = setInterval(() => {
                setProgress(p => Math.min(p + 5, 90));
            }, 200);

            const res = await axios.post(`${API_URL}/api/leads/import`, formData, {
                withCredentials: true,
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            clearInterval(progressInterval);
            setProgress(100);
            setResult(res.data);
            setStep('done');
        } catch (err) {
            setError(err.response?.data?.detail || 'Import failed');
            setStep('upload');
        } finally {
            setImporting(false);
        }
    };

    const handleComplete = () => {
        onSuccess();
        reset();
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-2xl max-h-[90vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle className="font-heading flex items-center gap-2">
                        <FileSpreadsheet size={20} className="text-[#E8536A]" />
                        Import Leads
                    </DialogTitle>
                </DialogHeader>

                <div className="flex-1 overflow-hidden">
                    {/* Upload Step */}
                    {step === 'upload' && (
                        <div className="space-y-4">
                            <div
                                className={`border-2 border-dashed rounded-[12px] p-8 text-center transition-colors ${
                                    dragActive 
                                        ? 'border-[#E8536A] bg-[#FFF5F5]' 
                                        : 'border-gray-200 hover:border-gray-300'
                                }`}
                                onDragEnter={handleDrag}
                                onDragLeave={handleDrag}
                                onDragOver={handleDrag}
                                onDrop={handleDrop}
                            >
                                <Upload size={40} className="mx-auto text-gray-400 mb-4" />
                                <p className="text-[13px] text-gray-600 mb-2">
                                    Drag and drop your file here, or
                                </p>
                                <label className="cursor-pointer">
                                    <span className="text-[#E8536A] font-medium hover:underline">browse</span>
                                    <input
                                        type="file"
                                        accept=".csv,.xlsx,.xls"
                                        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                                        className="hidden"
                                        data-testid="import-file-input"
                                    />
                                </label>
                                <p className="text-[11px] text-gray-400 mt-2">
                                    Supports CSV and Excel files (.csv, .xlsx, .xls)
                                </p>
                            </div>

                            {error && (
                                <div className="flex items-center gap-2 text-red-600 bg-red-50 px-3 py-2 rounded-lg text-[12px]">
                                    <AlertTriangle size={14} />
                                    {error}
                                </div>
                            )}

                            <div className="bg-gray-50 rounded-[10px] p-4">
                                <h4 className="text-[12px] font-medium text-gray-700 mb-2">Auto-detected columns:</h4>
                                <div className="text-[11px] text-gray-500 space-y-1">
                                    <p>Company Name, Phone, Phone 2, WhatsApp, Instagram, Email, City, Category, Priority, Assigned To, Notes, Response 1-3, Next Follow-up, Portfolio Sent, Pipeline Stage, Source</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Preview Step */}
                    {step === 'preview' && preview && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between bg-green-50 px-4 py-2 rounded-lg">
                                <div className="flex items-center gap-2">
                                    <Check size={16} className="text-green-600" />
                                    <span className="text-[12px] text-green-700">
                                        File loaded: <strong>{file?.name}</strong>
                                    </span>
                                </div>
                                <span className="text-[12px] font-medium text-green-700">
                                    {preview.totalRows} rows found
                                </span>
                            </div>

                            <div className="bg-gray-50 rounded-[10px] p-3">
                                <h4 className="text-[11px] font-medium text-gray-700 mb-2">Column Mapping</h4>
                                <div className="flex flex-wrap gap-2">
                                    {Object.entries(preview.columnMapping).map(([orig, mapped]) => (
                                        <span key={orig} className="text-[10px] bg-white px-2 py-1 rounded border border-gray-200">
                                            {orig} <ChevronRight size={10} className="inline" /> <span className="font-medium text-[#E8536A]">{mapped}</span>
                                        </span>
                                    ))}
                                </div>
                                {preview.unmappedColumns?.length > 0 && (
                                    <p className="text-[10px] text-gray-400 mt-2">
                                        Ignored columns: {preview.unmappedColumns.join(', ')}
                                    </p>
                                )}
                            </div>

                            <div>
                                <h4 className="text-[11px] font-medium text-gray-700 mb-2">Preview (first 10 rows)</h4>
                                <ScrollArea className="h-[200px] border border-gray-100 rounded-lg">
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-[10px]">
                                            <thead className="bg-gray-50 sticky top-0">
                                                <tr>
                                                    {preview.columns.map(col => (
                                                        <th key={col} className="px-2 py-1.5 text-left font-medium text-gray-600 whitespace-nowrap">
                                                            {col}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {preview.preview.map((row, idx) => (
                                                    <tr key={idx} className="border-t border-gray-50">
                                                        {preview.columns.map(col => (
                                                            <td key={col} className="px-2 py-1 text-gray-700 whitespace-nowrap max-w-[150px] truncate">
                                                                {String(row[col] || '')}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </ScrollArea>
                            </div>

                            <div className="flex justify-end gap-2">
                                <Button variant="outline" onClick={reset} className="rounded-[8px]">
                                    Cancel
                                </Button>
                                <Button 
                                    onClick={handleImport}
                                    className="bg-[#E8536A] hover:bg-[#D43D54] text-white rounded-[8px]"
                                    data-testid="confirm-import-btn"
                                >
                                    Import {preview.totalRows} Leads
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* Importing Step */}
                    {step === 'importing' && (
                        <div className="text-center py-8">
                            <div className="w-16 h-16 border-4 border-[#E8536A] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                            <p className="text-[13px] text-gray-600 mb-4">
                                Importing leads... Please don't close this window.
                            </p>
                            <Progress value={progress} className="w-full max-w-xs mx-auto" />
                            <p className="text-[11px] text-gray-400 mt-2">{progress}%</p>
                        </div>
                    )}

                    {/* Done Step */}
                    {step === 'done' && result && (
                        <div className="space-y-4">
                            <div className="text-center py-4">
                                <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                                    <Check size={32} className="text-green-600" />
                                </div>
                                <h3 className="font-heading text-lg font-semibold text-gray-900">Import Complete!</h3>
                            </div>

                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-green-50 rounded-[10px] p-4 text-center">
                                    <p className="text-2xl font-bold text-green-600">{result.imported}</p>
                                    <p className="text-[11px] text-green-700">Imported</p>
                                </div>
                                <div className="bg-amber-50 rounded-[10px] p-4 text-center">
                                    <p className="text-2xl font-bold text-amber-600">{result.duplicatesSkipped}</p>
                                    <p className="text-[11px] text-amber-700">Duplicates Skipped</p>
                                </div>
                                <div className="bg-red-50 rounded-[10px] p-4 text-center">
                                    <p className="text-2xl font-bold text-red-600">{result.totalErrors}</p>
                                    <p className="text-[11px] text-red-700">Errors</p>
                                </div>
                            </div>

                            {result.errors?.length > 0 && (
                                <div className="bg-red-50 rounded-[10px] p-3">
                                    <h4 className="text-[11px] font-medium text-red-700 mb-2">Errors (first 10)</h4>
                                    <ScrollArea className="h-[100px]">
                                        <ul className="text-[10px] text-red-600 space-y-1">
                                            {result.errors.slice(0, 10).map((err, idx) => (
                                                <li key={idx}>Row {err.row}: {err.reason}</li>
                                            ))}
                                        </ul>
                                    </ScrollArea>
                                </div>
                            )}

                            <div className="flex justify-end">
                                <Button 
                                    onClick={handleComplete}
                                    className="bg-[#E8536A] hover:bg-[#D43D54] text-white rounded-[8px]"
                                    data-testid="import-done-btn"
                                >
                                    Done
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
