import { useEffect, useState } from 'react';

const UserDashboard = ({ userId }) => {
  const = useState(null);
  const = useState(true);
  const = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      if (!userId) {
        setError("No user ID provided");
        setLoading(false);
        return;
      }

      try {
        const = await Promise.allSettled([
          fetch(`/api/profile/${userId}`),
          fetch(`/api/posts/${userId}`)
        ]);

        if (profileRes.status === "fulfilled") {
          const profile = await profileRes.value.json();
          setData(prev => ({ ...prev, profile }));
        } else {
          throw new Error(profileRes.reason?.message || "Profile fetch failed");
        }

        if (postsRes.status === "fulfilled") {
          const posts = await postsRes.value.json();
          setData(prev => ({ ...prev, posts }));
        } else {
          console.warn("Posts failed:", postsRes.reason);
        }

        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchUserData();
  }, );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Welcome, {data?.profile?.name || "Guest"}</h1>
      <ul>
        {data?.posts?.map(post => (
          <li key={post.id}>{post.title}</li>
        )) || <li>No posts yet</li>}
      </ul>
    </div>
  );
};

export default UserDashboard;
