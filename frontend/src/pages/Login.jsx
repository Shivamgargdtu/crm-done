import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Loader2, Heart } from 'lucide-react';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const result = await login(email, password);
        
        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-[#FFF5F5] flex items-center justify-center p-4">
            <div className="w-full max-w-sm">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#E8536A] mb-4">
                        <Heart className="w-8 h-8 text-white" fill="white" />
                    </div>
                    <h1 className="font-heading text-2xl font-semibold text-gray-900">Wed Us CRM</h1>
                    <p className="text-[13px] text-gray-500 mt-1">Wedding Design Company CRM</p>
                </div>

                {/* Login Card */}
                <div className="bg-white rounded-[16px] shadow-[0_2px_12px_rgba(232,83,106,0.06)] border border-gray-100 p-6">
                    <h2 className="font-heading text-lg font-medium text-gray-900 mb-6">Sign in to your account</h2>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="email" className="text-[13px] font-medium text-gray-700">
                                Email
                            </Label>
                            <Input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="admin@wedus.com"
                                required
                                data-testid="login-email-input"
                                className="h-10 rounded-[10px] border-gray-200 focus:border-[#E8536A] focus:ring-[#E8536A]/20"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password" className="text-[13px] font-medium text-gray-700">
                                Password
                            </Label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                data-testid="login-password-input"
                                className="h-10 rounded-[10px] border-gray-200 focus:border-[#E8536A] focus:ring-[#E8536A]/20"
                            />
                        </div>

                        {error && (
                            <div className="text-[13px] text-red-600 bg-red-50 px-3 py-2 rounded-lg" data-testid="login-error">
                                {error}
                            </div>
                        )}

                        <Button
                            type="submit"
                            disabled={loading}
                            data-testid="login-submit-btn"
                            className="w-full h-10 bg-[#E8536A] hover:bg-[#D43D54] text-white rounded-[12px] font-medium transition-colors"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </Button>
                    </form>
                </div>

                <p className="text-center text-[11px] text-gray-400 mt-6">
                    © 2024 Wed Us CRM. All rights reserved.
                </p>
            </div>
        </div>
    );
}
