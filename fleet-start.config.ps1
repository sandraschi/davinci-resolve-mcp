# Per-repo fleet start config for davinci-resolve-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'davinci-resolve-mcp'
    BackendPort  = 10843
    FrontendPort = 10842
    HealthPath   = '/api/v1/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'davinci_resolve_mcp.server:api_app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10843' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
