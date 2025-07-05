import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Card,
  CardContent,
  Grid,
  IconButton,
  Tooltip,
  Snackbar,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  OpenInNew as OpenIcon,
  Analytics as AnalyticsIcon,
  Link as LinkIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [formData, setFormData] = useState({
    url: '',
    validity: 30,
    shortcode: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'validity' ? parseInt(value) || 30 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    setAnalytics(null);

    try {
      const payload = {
        url: formData.url,
        validity: formData.validity
      };

      if (formData.shortcode.trim()) {
        payload.shortcode = formData.shortcode.trim();
      }

      const response = await axios.post(`${API_BASE_URL}/shorturls`, payload);
      setResult(response.data);
      setSuccess('URL shortened successfully!');
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'An error occurred while shortening the URL';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccess('Copied to clipboard!');
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

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        {/* Header */}
        <Box textAlign="center" mb={4}>
          <LinkIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h3" component="h1" gutterBottom>
            URL Shortener
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create short, shareable links with analytics
          </Typography>
        </Box>

        {/* Form */}
        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Long URL"
                name="url"
                value={formData.url}
                onChange={handleInputChange}
                placeholder="https://example.com/very-long-url"
                required
                variant="outlined"
                size="large"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Validity (minutes)"
                name="validity"
                type="number"
                value={formData.validity}
                onChange={handleInputChange}
                inputProps={{ min: 1, max: 1440 }}
                helperText="Default: 30 minutes"
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Custom Shortcode (optional)"
                name="shortcode"
                value={formData.shortcode}
                onChange={handleInputChange}
                placeholder="my-custom-link"
                helperText="3-20 alphanumeric characters"
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={loading || !formData.url}
                startIcon={loading ? <CircularProgress size={20} /> : <LinkIcon />}
              >
                {loading ? 'Creating Short URL...' : 'Create Short URL'}
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Success Alert */}
        {success && (
          <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Result Card */}
        {result && (
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Your Shortened URL
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TextField
                  fullWidth
                  value={result.shortLink}
                  variant="outlined"
                  size="small"
                  InputProps={{ readOnly: true }}
                  sx={{ mr: 1 }}
                />
                <Tooltip title="Copy URL">
                  <IconButton 
                    onClick={() => copyToClipboard(result.shortLink)}
                    color="primary"
                  >
                    <CopyIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Open URL">
                  <IconButton 
                    onClick={() => openUrl(result.shortLink)}
                    color="primary"
                  >
                    <OpenIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="View Analytics">
                  <IconButton 
                    onClick={() => getAnalytics(result.shortLink.split('/').pop())}
                    color="primary"
                  >
                    <AnalyticsIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                <TimeIcon sx={{ mr: 1, fontSize: 16 }} />
                <Typography variant="body2">
                  Expires: {formatDate(result.expiry)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Analytics Modal */}
        {analytics && showAnalytics && (
          <Card variant="outlined">
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
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
              
              {analytics.recent_accesses.length > 0 && (
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

export default App;
