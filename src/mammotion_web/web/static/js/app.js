async function logout(e){
  e.preventDefault();
  const res = await fetch('/api/logout',{method:'POST'});
  if(res.ok){ window.location.href='/login'; }
  return false;
}
