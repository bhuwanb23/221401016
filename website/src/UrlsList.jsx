import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Divider,
  Button
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  OpenInNew as OpenIcon,
  Analytics as AnalyticsIcon,
  Refresh as RefreshIcon,
  Link as LinkIcon,
  AccessTime as TimeIcon,
  Visibility as VisibilityIcon,
  CheckCircle as ActiveIcon,
  Cancel as ExpiredIcon,
  Warning as InactiveIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

function UrlsList() {
  const [urls, setUrls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);

  const fetchUrls = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axios.get(`${API_BASE_URL}/urls`);
      setUrls(response.data.urls);
    } catch (err) {
      setError('Failed to fetch URLs');
      console.error('Error fetching URLs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUrls();
  }, []);

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccess('Copied to clipboard!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to copy to clipboard');
    }
  };

  const openUrl = (url) => {
    window.open(url, '_blank');
  };

  const getAnalytics = async (shortcode) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/${shortcode}`);
      setAnalytics(response.data);
      setShowAnalytics(true);
    } catch (err) {
      setError('Failed to fetch analytics');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusChip = (url) => {
    if (url.is_expired) {
      return <Chip icon={<ExpiredIcon />} label="Expired" color="error" size="small" />;
    } else if (!url.is_active) {
      return <Chip icon={<InactiveIcon />} label="Inactive" color="warning" size="small" />;
    } else {
      return <Chip icon={<ActiveIcon />} label="Active" color="success" size="small" />;
    }
  };

  const truncateUrl = (url, maxLength = 50) => {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              URL Management
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage and monitor all shortened URLs
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchUrls}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {/* Alerts */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Stats Card */}
        <Card variant="outlined" sx={{ mb: 3 }} className="stats-card">
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {urls.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total URLs
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {urls.filter(url => !url.is_expired && url.is_active).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active URLs
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="error.main">
                    {urls.filter(url => url.is_expired).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expired URLs
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* URLs Table */}
        {urls.length === 0 ? (
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <LinkIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No URLs Found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Create your first shortened URL to get started
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'grey.50' }}>
                  <TableCell><strong>Short Link</strong></TableCell>
                  <TableCell><strong>Shortened URL</strong></TableCell>
                  <TableCell><strong>Original URL</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell><strong>Created</strong></TableCell>
                  <TableCell><strong>Expires</strong></TableCell>
                  <TableCell><strong>Accesses</strong></TableCell>
                  <TableCell><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {urls.map((url) => (
                                     <TableRow key={url.id} hover>
                     <TableCell>
                       <Box display="flex" alignItems="center">
                         <Typography variant="body2" fontFamily="monospace" sx={{ mr: 1, fontWeight: 600 }}>
                           {url.shortcode}
                         </Typography>
                         <Tooltip title="Copy shortcode">
                           <IconButton
                             size="small"
                             onClick={() => copyToClipboard(url.shortcode)}
                           >
                             <CopyIcon fontSize="small" />
                           </IconButton>
                         </Tooltip>
                       </Box>
                     </TableCell>
                     <TableCell>
                       <Box display="flex" alignItems="center">
                         <Typography variant="body2" fontFamily="monospace" sx={{ 
                           mr: 1, 
                           fontWeight: 500,
                           color: '#1976d2',
                           textDecoration: 'underline',
                           cursor: 'pointer'
                         }} onClick={() => copyToClipboard(url.short_link)}>
                           {url.short_link}
                         </Typography>
                         <Tooltip title="Copy shortened URL">
                           <IconButton
                             size="small"
                             onClick={() => copyToClipboard(url.short_link)}
                           >
                             <CopyIcon fontSize="small" />
                           </IconButton>
                         </Tooltip>
                       </Box>
                     </TableCell>
                     <TableCell>
                       <Tooltip title={url.original_url}>
                         <Typography variant="body2" sx={{ maxWidth: 200 }}>
                           {truncateUrl(url.original_url)}
                         </Typography>
                       </Tooltip>
                     </TableCell>
                    <TableCell>
                      {getStatusChip(url)}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(url.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <TimeIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          {formatDate(url.expires_at)}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <VisibilityIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          {url.access_count}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5}>
                        <Tooltip title="Open short link">
                          <IconButton
                            size="small"
                            onClick={() => openUrl(url.short_link)}
                            disabled={url.is_expired}
                          >
                            <OpenIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View analytics">
                          <IconButton
                            size="small"
                            onClick={() => getAnalytics(url.shortcode)}
                          >
                            <AnalyticsIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Analytics Modal */}
        {analytics && showAnalytics && (
          <Card variant="outlined" sx={{ mt: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Analytics for {analytics.shortcode}
                </Typography>
                <Button 
                  size="small" 
                  onClick={() => setShowAnalytics(false)}
                >
                  Close
                </Button>
              </Box>
              
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Original URL
                  </Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                    {analytics.original_url}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Accesses
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {analytics.total_accesses}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(analytics.created_at)}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Expires
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(analytics.expires_at)}
                  </Typography>
                </Grid>
              </Grid>
              
              {analytics.recent_accesses && analytics.recent_accesses.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Recent Accesses
                  </Typography>
                  {analytics.recent_accesses.map((access, index) => (
                    <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="body2">
                        <strong>Time:</strong> {formatDate(access.accessed_at)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>IP:</strong> {access.ip_address}
                      </Typography>
                    </Box>
                  ))}
                </>
              )}
            </CardContent>
          </Card>
        )}
      </Paper>
    </Container>
  );
}

export default UrlsList; 