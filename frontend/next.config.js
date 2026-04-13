/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        
        // Remove trailing slash if present
        apiUrl = apiUrl.replace(/\/$/, '');
        
        // Remove accidental /api suffix if present
        apiUrl = apiUrl.replace(/\/api$/, '');
        
        console.log('Rewriting /api/* to:', `${apiUrl}/*`);

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/:path*`
            }
        ];
    }
};

module.exports = nextConfig;
