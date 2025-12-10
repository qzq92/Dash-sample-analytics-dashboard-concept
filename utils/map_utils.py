"""
Map utility functions for common map configurations.
"""


def get_onemap_attribution():
    """
    Get the standard OneMap attribution string used across all maps.
    
    Returns:
        String containing HTML attribution with OneMap logo, link, and SLA link
    """
    return '''<img src="https://www.onemap.gov.sg/web-assets/images/logo/om_logo.png" style="height:20px;width:20px;"/>&nbsp;<a href="https://www.onemap.gov.sg/" target="_blank" rel="noopener noreferrer">OneMap</a>&nbsp;&copy;&nbsp;contributors&nbsp;&#124;&nbsp;<a href="https://www.sla.gov.sg/" target="_blank" rel="noopener noreferrer">Singapore Land Authority</a>'''

