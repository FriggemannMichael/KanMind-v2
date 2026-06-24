"""auth_app defines no custom permissions.

  Registration and login are public (AllowAny); every other endpoint relies
  on the project-wide TokenAuthentication and IsAuthenticated defaults.
  """
