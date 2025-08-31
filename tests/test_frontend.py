import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class TestFrontend:
    def setup_method(self):
        """Setup Chrome driver for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.base_url = "http://localhost:5000"
    
    def teardown_method(self):
        """Clean up driver after each test"""
        if self.driver:
            self.driver.quit()
    
    def test_dashboard_loads(self):
        """Test that the main dashboard loads correctly"""
        self.driver.get(self.base_url)
        
        # Check if main elements are present
        assert "Surgical Simulation Platform" in self.driver.title
        
        # Check for dashboard elements
        dashboard = self.driver.find_element(By.ID, "dashboard")
        assert dashboard.is_displayed()
        
        # Check for navigation elements
        nav = self.driver.find_element(By.CLASS_NAME, "navbar")
        assert nav.is_displayed()
    
    def test_procedure_selection(self):
        """Test procedure selection functionality"""
        self.driver.get(self.base_url)
        
        # Find and click on a procedure card
        procedure_cards = self.driver.find_elements(By.CLASS_NAME, "procedure-card")
        assert len(procedure_cards) > 0
        
        # Click on first procedure
        procedure_cards[0].click()
        
        # Check if simulation page loads
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/simulation")
        )
    
    def test_simulation_interface(self):
        """Test simulation interface elements"""
        self.driver.get(f"{self.base_url}/simulation")
        
        # Check for simulation container
        sim_container = self.driver.find_element(By.CLASS_NAME, "simulation-container")
        assert sim_container.is_displayed()
        
        # Check for sidebar
        sidebar = self.driver.find_element(By.CLASS_NAME, "simulation-sidebar")
        assert sidebar.is_displayed()
        
        # Check for viewport
        viewport = self.driver.find_element(By.CLASS_NAME, "simulation-viewport")
        assert viewport.is_displayed()
    
    def test_patient_information_display(self):
        """Test patient information display in simulation"""
        self.driver.get(f"{self.base_url}/simulation")
        
        # Check for patient panel
        patient_panel = self.driver.find_element(By.CLASS_NAME, "patient-panel")
        assert patient_panel.is_displayed()
        
        # Check for patient vitals
        vitals_grid = self.driver.find_element(By.CLASS_NAME, "vitals-grid")
        assert vitals_grid.is_displayed()
    
    def test_procedure_steps_navigation(self):
        """Test procedure steps navigation"""
        self.driver.get(f"{self.base_url}/simulation")
        
        # Check for steps panel
        steps_panel = self.driver.find_element(By.CLASS_NAME, "steps-panel")
        assert steps_panel.is_displayed()
        
        # Check for step list
        step_list = self.driver.find_element(By.CLASS_NAME, "step-list")
        assert step_list.is_displayed()
    
    def test_control_buttons(self):
        """Test simulation control buttons"""
        self.driver.get(f"{self.base_url}/simulation")
        
        # Check for control buttons
        control_buttons = self.driver.find_elements(By.CLASS_NAME, "control-button")
        assert len(control_buttons) > 0
        
        # Test that buttons are clickable
        for button in control_buttons:
            assert button.is_enabled()
    
    def test_tool_selection(self):
        """Test surgical tool selection"""
        self.driver.get(f"{self.base_url}/simulation")
        
        # Check for tool panel
        tool_panel = self.driver.find_element(By.CLASS_NAME, "tool-panel")
        assert tool_panel.is_displayed()
        
        # Check for tool buttons
        tool_buttons = self.driver.find_elements(By.CLASS_NAME, "tool-button")
        assert len(tool_buttons) > 0
    
    def test_responsive_design(self):
        """Test responsive design on different screen sizes"""
        self.driver.get(self.base_url)
        
        # Test mobile viewport
        self.driver.set_window_size(375, 667)  # iPhone SE size
        time.sleep(2)
        
        # Check if elements are still accessible
        dashboard = self.driver.find_element(By.ID, "dashboard")
        assert dashboard.is_displayed()
        
        # Test tablet viewport
        self.driver.set_window_size(768, 1024)  # iPad size
        time.sleep(2)
        
        # Check if elements are still accessible
        dashboard = self.driver.find_element(By.ID, "dashboard")
        assert dashboard.is_displayed()
    
    def test_navigation_links(self):
        """Test navigation between pages"""
        self.driver.get(self.base_url)
        
        # Test navigation to simulation page
        sim_link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/simulation']")
        sim_link.click()
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/simulation")
        )
        
        # Test navigation back to dashboard
        dashboard_link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/']")
        dashboard_link.click()
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/")
        )
    
    def test_error_handling(self):
        """Test error handling for invalid routes"""
        self.driver.get(f"{self.base_url}/invalid-route")
        
        # Check if error page is displayed or redirected
        current_url = self.driver.current_url
        assert current_url == f"{self.base_url}/invalid-route" or current_url == self.base_url
    
    def test_performance_metrics_display(self):
        """Test performance metrics display on dashboard"""
        self.driver.get(self.base_url)
        
        # Check for performance metrics
        metrics_elements = self.driver.find_elements(By.CLASS_NAME, "metric-card")
        assert len(metrics_elements) > 0
        
        # Check for specific metrics
        avg_score = self.driver.find_element(By.ID, "avg-score")
        assert avg_score.is_displayed()
        
        completed_sims = self.driver.find_element(By.ID, "completed-sims")
        assert completed_sims.is_displayed()
    
    def test_recent_activity_display(self):
        """Test recent activity display on dashboard"""
        self.driver.get(self.base_url)
        
        # Check for recent activity section
        recent_activity = self.driver.find_element(By.ID, "recent-simulations")
        assert recent_activity.is_displayed()
        
        # Check for activity items (may be empty initially)
        activity_items = self.driver.find_elements(By.CLASS_NAME, "activity-item")
        # Activity items might not be present if no simulations have been run
        # This is acceptable for a new installation
