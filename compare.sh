printf "%-10s %-50s %-64s %-16s\n" "STATUS" "BASE FILE" "SHA-256 HASH" "MAGIC BYTES"
printf "%-10s %-50s %-64s %-16s\n" "----------" "--------------------------------------------------" "----------------------------------------------------------------" "----------------"

find . -name "*.old.dec" -print0 | while IFS= read -r -d '' old_file; do
  base="${old_file%.old.dec}"
  base_hash=$(sha256sum "$base" | awk '{print $1}')
  old_hash=$(sha256sum "$old_file" | awk '{print $1}')
  
  # Extract the first 16 bytes as a string
  magic_bytes=$(head -c 16 "$base" 2>/dev/null | tr -cd '[:print:]' || echo "N/A")
  
  if [ ! -f "$base.new.dec" ]; then
    printf "%-10s %-50s %-64s %-16s\n" "MISSING" "$base" "$base_hash" "$magic_bytes"
    continue
  fi
  
  new_hash=$(sha256sum "$base.new.dec" | awk '{print $1}')
  if [ "$new_hash" = "$old_hash" ]; then
    printf "%-10s %-50s %-64s %-16s\n" "IDENTICAL" "$base" "$base_hash" "$magic_bytes"
  else
    printf "%-10s %-50s %-64s %-16s\n" "DIFFERENT" "$base" "$base_hash" "$magic_bytes"
  fi
done | sort
